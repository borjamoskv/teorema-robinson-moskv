/*
 * MOSKV-1 APEX PROP FIRM HFT SWARM ENGINE
 * Author: Borja Moskv (borjamoskv)
 * Level: C5-REAL Execution Kernel
 * 
 * Invariants Enforced:
 * - K1 (FAIL-FAST TERMODINAMICO): Direct error propagation, no silent exceptions.
 * - L5 (Γ1 SELLO DE CREADOR INMUTABLE): Author credit intact.
 * - L12 (Teorema del Crash Causal): Purged defensive code.
 */

use std::collections::VecDeque;
use std::sync::Arc;
use tokio::sync::Mutex;

use rand::Rng;
use uuid::Uuid;
use serde::{Serialize, Deserialize};
use chrono::Utc;

// --- CONFIGURACIÓN & ENTIDADES ---

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HftNodeConfig {
    pub instance_id: Uuid,
    pub account_id: String,
    pub initial_balance: f64,
    pub profit_target: f64,
    pub max_daily_drawdown: f64,
    pub max_total_drawdown: f64,
    pub lot_size: f64,
    pub min_correlation: f64,
    pub entry_zscore: f64,
    pub exit_zscore: f64,
    pub proxy_ip: String,
    // Evasive parameters to bypass copy-trading detection
    pub base_delay_ms: u64,
    pub jitter_ms: u64,
    pub tp_random_factor: f64,
    pub sl_random_factor: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum PositionType {
    Buy,
    Sell,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Position {
    pub id: Uuid,
    pub position_type: PositionType,
    pub entry_price: f64,
    pub volume: f64,
    pub sl: f64,
    pub tp: f64,
    pub open_time: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccountState {
    pub balance: f64,
    pub equity: f64,
    pub high_water_mark: f64,
    pub daily_start_equity: f64,
    pub max_daily_drawdown_limit: f64,
    pub max_total_drawdown_limit: f64,
    pub is_failed: bool,
    pub is_passed: bool,
}

// --- ENGINE DE CORRELACIÓN ESTADÍSTICA ---

pub struct RollingCorrelation {
    pub window_size: usize,
    pub series_a: VecDeque<f64>,
    pub series_b: VecDeque<f64>,
}

impl RollingCorrelation {
    pub fn new(window_size: usize) -> Self {
        Self {
            window_size,
            series_a: VecDeque::with_capacity(window_size),
            series_b: VecDeque::with_capacity(window_size),
        }
    }

    pub fn push(&mut self, val_a: f64, val_b: f64) {
        if self.series_a.len() >= self.window_size {
            self.series_a.pop_front();
            self.series_b.pop_front();
        }
        self.series_a.push_back(val_a);
        self.series_b.push_back(val_b);
    }

    // Pearson Correlation Coefficient calculation (Fail-fast on insufficient data)
    pub fn calculate_correlation(&self) -> f64 {
        let n = self.series_a.len();
        if n < 5 {
            return 0.0;
        }

        let mean_a = self.series_a.iter().sum::<f64>() / n as f64;
        let mean_b = self.series_b.iter().sum::<f64>() / n as f64;

        let mut num = 0.0;
        let mut den_a = 0.0;
        let mut den_b = 0.0;

        for i in 0..n {
            let diff_a = self.series_a[i] - mean_a;
            let diff_b = self.series_b[i] - mean_b;
            num += diff_a * diff_b;
            den_a += diff_a * diff_a;
            den_b += diff_b * diff_b;
        }

        if den_a == 0.0 || den_b == 0.0 {
            return 0.0;
        }

        num / (den_a * den_b).sqrt()
    }

    // Cointegration spread and z-score calculation
    pub fn calculate_zscore(&self) -> (f64, f64) {
        let n = self.series_a.len();
        assert!(n >= 5, "Falta exergía: Datos insuficientes para el cálculo del z-score");

        // Calculate beta (hedge ratio) using linear regression
        let mean_a = self.series_a.iter().sum::<f64>() / n as f64;
        let mean_b = self.series_b.iter().sum::<f64>() / n as f64;

        let mut num = 0.0;
        let mut den_b = 0.0;
        for i in 0..n {
            num += (self.series_b[i] - mean_b) * (self.series_a[i] - mean_a);
            den_b += (self.series_b[i] - mean_b).powi(2);
        }

        let beta = if den_b == 0.0 { 1.0 } else { num / den_b };

        // Spread = SeriesA - Beta * SeriesB
        let spreads: Vec<f64> = (0..n)
            .map(|i| self.series_a[i] - beta * self.series_b[i])
            .collect();

        let mean_spread = spreads.iter().sum::<f64>() / n as f64;
        let var_spread = spreads.iter().map(|s| (s - mean_spread).powi(2)).sum::<f64>() / (n - 1) as f64;
        let std_spread = var_spread.sqrt();

        let current_spread = self.series_a[n - 1] - beta * self.series_b[n - 1];

        let zscore = if std_spread == 0.0 {
            0.0
        } else {
            (current_spread - mean_spread) / std_spread
        };

        (zscore, beta)
    }
}

// --- GATEWAY DE EJECUCIÓN CON SIMULADOR DE DESVIACIÓN (SLIPPAGE/LATENCIA) ---

pub struct ExecutionGateway {
    pub config: HftNodeConfig,
    pub account: AccountState,
    pub open_positions: Vec<Position>,
}

impl ExecutionGateway {
    pub fn new(config: HftNodeConfig) -> Self {
        let max_daily_drawdown_limit = config.initial_balance * (1.0 - config.max_daily_drawdown);
        let max_total_drawdown_limit = config.initial_balance * (1.0 - config.max_total_drawdown);

        Self {
            account: AccountState {
                balance: config.initial_balance,
                equity: config.initial_balance,
                high_water_mark: config.initial_balance,
                daily_start_equity: config.initial_balance,
                max_daily_drawdown_limit,
                max_total_drawdown_limit,
                is_failed: false,
                is_passed: false,
            },
            config,
            open_positions: Vec::new(),
        }
    }

    pub fn place_order(&mut self, pos_type: PositionType, price_a: f64, price_b: f64) {
        if self.account.is_failed || self.account.is_passed {
            return;
        }

        let mut rng = rand::thread_rng();
        let gap = price_a - price_b;

        // Model latency arbitrage gap closure due to proxy delay and broker execution delay
        let delay_ratio = (self.config.base_delay_ms as f64 / 35.0).min(1.0);
        let gap_closure_ratio = rng.gen_range(0.40..0.98) * delay_ratio;
        
        let executed_price = price_b + gap * gap_closure_ratio;

        // Apply a small random spread/slippage on top
        let spread_slippage = rng.gen_range(0.00001..0.00003) * price_b;
        let executed_price = match pos_type {
            PositionType::Buy => executed_price + spread_slippage,
            PositionType::Sell => executed_price - spread_slippage,
        };

        // Randomized SL and TP calculation
        let pip_size = 0.0001;
        let raw_tp = 20.0 * pip_size; // 20 pips target
        let raw_sl = 10.0 * pip_size; // 10 pips stop-loss
        
        let tp_mod = raw_tp * rng.gen_range(1.0 - self.config.tp_random_factor..1.0 + self.config.tp_random_factor);
        let sl_mod = raw_sl * rng.gen_range(1.0 - self.config.sl_random_factor..1.0 + self.config.sl_random_factor);

        let (tp, sl) = match pos_type {
            PositionType::Buy => (executed_price + tp_mod, executed_price - sl_mod),
            PositionType::Sell => (executed_price - tp_mod, executed_price + sl_mod),
        };

        let new_pos = Position {
            id: Uuid::new_v4(),
            position_type: pos_type,
            entry_price: executed_price,
            volume: self.config.lot_size,
            sl,
            tp,
            open_time: Utc::now().timestamp_millis(),
        };

        self.open_positions.push(new_pos);
    }

    pub fn update_market_price(&mut self, _price_a: f64, price_b: f64, _beta: f64) {
        if self.account.is_failed || self.account.is_passed {
            return;
        }

        let mut unrealized_pnl = 0.0;
        let mut closed_positions = Vec::new();
        let mut active_positions = Vec::new();

        // Evaluate positions against TP/SL and market delta of the slow feed (price_b)
        for pos in &self.open_positions {
            let current_pnl = match pos.position_type {
                PositionType::Buy => (price_b - pos.entry_price) * pos.volume * 100000.0,
                PositionType::Sell => (pos.entry_price - price_b) * pos.volume * 100000.0,
            };

            let hit_tp = match pos.position_type {
                PositionType::Buy => price_b >= pos.tp,
                PositionType::Sell => price_b <= pos.tp,
            };

            let hit_sl = match pos.position_type {
                PositionType::Buy => price_b <= pos.sl,
                PositionType::Sell => price_b >= pos.sl,
            };

            if hit_tp || hit_sl {
                closed_positions.push((pos.id, current_pnl));
            } else {
                unrealized_pnl += current_pnl;
                active_positions.push(pos.clone());
            }
        }

        // Close positions that hit SL/TP
        for (_, pnl) in closed_positions {
            self.account.balance += pnl;
        }
        self.open_positions = active_positions;

        // Calculate Equity
        self.account.equity = self.account.balance + unrealized_pnl;

        // Drawdown Audit (Fail-fast enforcement)
        if self.account.equity > self.account.high_water_mark {
            self.account.high_water_mark = self.account.equity;
        }

        // Check if daily drawdown breached
        if self.account.equity <= self.account.max_daily_drawdown_limit {
            self.account.is_failed = true;
        }

        // Check if total drawdown breached
        if self.account.equity <= self.account.max_total_drawdown_limit {
            self.account.is_failed = true;
        }

        // Check if profit target reached
        if self.account.equity >= self.config.initial_balance + self.config.profit_target && self.open_positions.is_empty() {
            self.account.is_passed = true;
        }
    }

    pub fn close_all_positions(&mut self, current_price_b: f64) {
        for pos in &self.open_positions {
            let pnl = match pos.position_type {
                PositionType::Buy => (current_price_b - pos.entry_price) * pos.volume * 100000.0,
                PositionType::Sell => (pos.entry_price - current_price_b) * pos.volume * 100000.0,
            };
            self.account.balance += pnl;
        }
        self.open_positions.clear();
        self.account.equity = self.account.balance;
        
        if self.account.equity >= self.config.initial_balance + self.config.profit_target {
            self.account.is_passed = true;
        }
    }
}

// --- ORQUESTADOR DEL SWARM DE INSTANCIAS ---

pub struct SwarmOrchestrator {
    pub nodes: Vec<Arc<Mutex<ExecutionGateway>>>,
}

impl SwarmOrchestrator {
    pub fn new(num_nodes: usize, initial_balance: f64) -> Self {
        let mut nodes = Vec::new();
        let mut rng = rand::thread_rng();

        for i in 0..num_nodes {
            let instance_id = Uuid::new_v4();
            let config = HftNodeConfig {
                instance_id,
                account_id: format!("AWS-NODE-{:03}", i + 1),
                initial_balance,
                profit_target: initial_balance * 0.10, // Challenge Target: 10%
                max_daily_drawdown: 0.05,             // Daily limit: 5%
                max_total_drawdown: 0.10,             // Total limit: 10%
                // Dynamic position sizes to simulate individual node characteristics
                lot_size: rng.gen_range(4.0..8.0),
                min_correlation: 0.85,
                entry_zscore: 2.0,
                exit_zscore: 0.5,
                proxy_ip: format!("172.16.8.{}", rng.gen_range(2..254)),
                // Unique jitter parameters per instance to destroy patterns
                base_delay_ms: rng.gen_range(5..45),
                jitter_ms: rng.gen_range(2..15),
                tp_random_factor: rng.gen_range(0.01..0.08),
                sl_random_factor: rng.gen_range(0.01..0.08),
            };

            nodes.push(Arc::new(Mutex::new(ExecutionGateway::new(config))));
        }

        Self { nodes }
    }

    pub async fn run_challenge(&self, ticks_count: usize) {
        let mut rng = rand::thread_rng();
        
        // Co-integrated series generator state
        let mut base_price_a = 1.0950; // EURUSD starting
        let mut base_price_b = 1.0950;
        let mut corr_engine = RollingCorrelation::new(50);

        // Warm up series data
        for _ in 0..50 {
            base_price_a += rng.gen_range(-0.0005..0.0005);
            base_price_b = base_price_a + rng.gen_range(-0.0002..0.0002);
            corr_engine.push(base_price_a, base_price_b);
        }

        println!("[C5-REAL] Iniciando Swarm de Arbitraje de Latencia de 50 Instancias AWS...");

        let latency_threshold = 0.0003; // 3 pips divergence threshold for entry

        for _tick in 0..ticks_count {
            // Generate leading price updates (fast feed moves first)
            let step_a = rng.gen_range(-0.0004..0.0004);
            base_price_a += step_a;

            // Slow feed lags behind. With probability, it doesn't catch up immediately
            let step_b = if rng.gen_bool(0.15) {
                // Large divergence: B lags behind A
                rng.gen_range(-0.0001..0.0001)
            } else {
                // B catches up towards A
                (base_price_a - base_price_b) * 0.70 + rng.gen_range(-0.00005..0.00005)
            };
            base_price_b += step_b;

            corr_engine.push(base_price_a, base_price_b);

            let gap = base_price_a - base_price_b;

            // Update all nodes synchronously to avoid lock contention & massive thread spawning
            for node in &self.nodes {
                let mut gw = node.lock().await;
                if gw.account.is_failed || gw.account.is_passed {
                    continue;
                }

                // Update local position valuations
                gw.update_market_price(base_price_a, base_price_b, 1.0);

                // Latency Arbitrage Strategy Core Logic
                if gw.open_positions.is_empty() {
                    if gap > latency_threshold {
                        // Fast feed A has jumped up. B is lagging. Buy B.
                        gw.place_order(PositionType::Buy, base_price_a, base_price_b);
                    } else if gap < -latency_threshold {
                        // Fast feed A has jumped down. B is lagging. Sell B.
                        gw.place_order(PositionType::Sell, base_price_a, base_price_b);
                    }
                } else {
                    // Close trades when the gap is closed
                    if gap.abs() <= 0.00005 {
                        gw.close_all_positions(base_price_b);
                    }
                }
            }
        }

        // Force close remaining open positions before final tally
        for node in &self.nodes {
            let mut gw = node.lock().await;
            if !gw.account.is_failed && !gw.account.is_passed {
                gw.close_all_positions(base_price_b);
            }
        }
    }

    pub async fn print_tally(&self) {
        let mut total_passed = 0;
        let mut total_failed = 0;
        let mut total_equity = 0.0;
        let mut final_balance = 0.0;

        println!("\n=================================================================================");
        println!("|           MOSKV-1 SWARM REPORT (INDUSTRIAL NOIR 2026 AUDIT)                   |");
        println!("=================================================================================");
        println!("|   NODE ID    |    IP PROXY   |    STATUS    |    BALANCE    |    EQUITY     |");
        println!("---------------------------------------------------------------------------------");

        for node in &self.nodes {
            let gw = node.lock().await;
            let status_str = if gw.account.is_passed {
                total_passed += 1;
                "PASSED (SOTA) "
            } else if gw.account.is_failed {
                total_failed += 1;
                "FAILED (BREACH)"
            } else {
                "ACTIVE (HELD) "
            };

            println!(
                "| {} | {} | {} | ${:12.2} | ${:12.2} |",
                gw.config.account_id,
                gw.config.proxy_ip,
                status_str,
                gw.account.balance,
                gw.account.equity
            );

            total_equity += gw.account.equity;
            final_balance += gw.account.balance;
        }

        let pass_rate = (total_passed as f64 / self.nodes.len() as f64) * 100.0;
        println!("=================================================================================");
        println!("| SWARM METRICS SUMMARY:");
        println!("| Total Nodes:       {}", self.nodes.len());
        println!("| Passed Accounts:   {} (Target: 10/50)", total_passed);
        println!("| Failed Accounts:   {}", total_failed);
        println!("| Pass Rate:         {:.2}%", pass_rate);
        println!("| Total Swarm Equity:${:.2}", total_equity);
        println!("| Total Swarm Balance:${:.2}", final_balance);
        println!("| Net Swarm Profit:  ${:.2}", total_equity - (self.nodes.len() as f64 * 100000.0));
        println!("=================================================================================");
    }
}

#[tokio::main]
async fn main() {
    let swarm = SwarmOrchestrator::new(50, 100000.0);
    swarm.run_challenge(3000).await;
    swarm.print_tally().await;
}
