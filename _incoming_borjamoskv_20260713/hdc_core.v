// hdc_core.v - HDC Associative Search Core (C5-REAL)
// Arquitectura de búsqueda asociativa con pipeline popcount determinista.
// MOSKV-1 APEX Kernel Soberano. Sintetizable RTL puro.

`timescale 1ns / 1ps

module hdc_core #(
    parameter integer D               = 16384,
    parameter integer CODEBOOK_DEPTH  = 10000,
    parameter integer POPCOUNT_STAGES = 14,   // profundidad pipeline popcount (log2(D))
    parameter integer ADDR_WIDTH      = $clog2(CODEBOOK_DEPTH)
)(
    input  wire                   clk,
    input  wire                   rst_n,
    input  wire                   start,
    input  wire [D-1:0]           query,
    output reg                    done,
    output reg  [ADDR_WIDTH-1:0]  match_idx,
    output reg  [13:0]            match_dist, // 14 bits para hasta 16384
    // Interfaz externa al codebook SRAM (o modelo Blackbox)
    output reg                    codebook_rd_en,
    output reg  [ADDR_WIDTH-1:0]  codebook_rd_addr,
    input  wire [D-1:0]           codebook_rd_data
);

    // ------------------------------------------------------------------------
    // Pipeline Popcount: árbol binario de sumadores con registros en cada etapa
    // ------------------------------------------------------------------------
    wire [D-1:0]            xor_vec = query ^ codebook_rd_data;
    wire [13:0]             popcount_result;

    popcount_pipe #(
        .WIDTH(D),
        .STAGES(POPCOUNT_STAGES)
    ) popcount_inst (
        .clk      (clk),
        .rst_n    (rst_n),
        .data_in  (xor_vec),
        .data_out (popcount_result)
    );

    // ------------------------------------------------------------------------
    // FSM de búsqueda asociativa (min distance, single cycle compare)
    // ------------------------------------------------------------------------
    localparam [1:0] IDLE   = 2'b00,
                     SEARCH = 2'b01,
                     DONE   = 2'b10;

    reg [1:0] state, nxt_state;

    // Contadores de dirección y de resultados procesados
    reg [ADDR_WIDTH-1:0] rd_addr;
    reg [ADDR_WIDTH:0]   result_cnt;   // para CODEBOOK_DEPTH+1 para no overflow
    reg                  search_active;

    // Pipeline de alineamiento de la salida popcount a la FSM
    // La latencia se absorbe en el pipeline interno de popcount.
    // Resultado aparece POPCOUNT_STAGES ciclos después de que data_in está estable.
    // Como la lectura de SRAM tiene 1 ciclo de latencia, la latencia total es POPCOUNT_STAGES+1.
    localparam integer TOTAL_LAT = POPCOUNT_STAGES + 1;
    reg [TOTAL_LAT-1:0] pipe_valid;  // desplazamiento

    // Registro de mínimo parcial e índice del pipeline de salida
    reg [13:0]            min_dist;
    reg [ADDR_WIDTH-1:0]  min_idx;
    reg [ADDR_WIDTH-1:0]  result_idx; // Índice del resultado actual en la salida

    // ----------------------------------------------------------------
    // Lógica secuencial de la FSM
    // ----------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= IDLE;
            rd_addr      <= 0;
            result_cnt   <= 0;
            result_idx   <= 0;
            pipe_valid   <= 0;
            min_dist     <= 14'h3FFF; // max valor (16383)
            min_idx      <= 0;
            done         <= 1'b0;
            match_idx    <= 0;
            match_dist   <= 0;
            codebook_rd_en   <= 1'b0;
            codebook_rd_addr <= 0;
            search_active    <= 1'b0;
        end else begin
            state <= nxt_state;

            case (state)
                IDLE: begin
                    done <= 1'b0;
                    if (start) begin
                        rd_addr      <= 0;
                        result_cnt   <= 0;
                        result_idx   <= 0;
                        pipe_valid   <= 0;
                        min_dist     <= 14'h3FFF;
                        min_idx      <= 0;
                        search_active<= 1'b1;
                        codebook_rd_en <= 1'b1;  // primer acceso
                        codebook_rd_addr <= 0;
                    end else begin
                        codebook_rd_en <= 1'b0;
                        search_active  <= 1'b0;
                    end
                end

                SEARCH: begin
                    // Control de direcciones de SRAM
                    if (rd_addr < CODEBOOK_DEPTH - 1) begin
                        codebook_rd_en   <= 1'b1;
                        codebook_rd_addr <= rd_addr + 1;
                        rd_addr          <= rd_addr + 1;
                    end else begin
                        codebook_rd_en   <= 1'b0;
                        // no incrementa más
                    end

                    // Tubería de validación para resultado popcount: propagamos el rd_en
                    pipe_valid <= {pipe_valid[TOTAL_LAT-2:0], codebook_rd_en};

                    // Contador de resultados útiles y comparación
                    if (pipe_valid[TOTAL_LAT-1]) begin
                        result_cnt <= result_cnt + 1;
                        result_idx <= result_idx + 1;
                        if (popcount_result < min_dist) begin
                            min_dist <= popcount_result;
                            min_idx  <= result_idx;
                        end
                    end

                    // Condición de finalización: todos los vectores procesados
                    if (result_cnt == CODEBOOK_DEPTH - 1 && pipe_valid[TOTAL_LAT-1]) begin
                        search_active <= 1'b0;
                    end
                end

                DONE: begin
                    done      <= 1'b1;
                    match_idx  <= min_idx;
                    match_dist <= min_dist;
                    codebook_rd_en <= 1'b0;
                    search_active  <= 1'b0;
                end
            endcase
        end
    end

    // Transiciones de la FSM
    always @(*) begin
        nxt_state = state;
        case (state)
            IDLE:   if (start) nxt_state = SEARCH;
            SEARCH: if (!search_active && result_cnt == CODEBOOK_DEPTH) nxt_state = DONE;
            DONE:   nxt_state = IDLE;
        endcase
    end

endmodule


// ===========================================================================
// Pipeline popcount: árbol binario de sumadores con STAGES etapas.
// Entrada: D bits; Salida: 14 bits (max 16384) tras STAGES ciclos.
// Topología: cada etapa combina pares de sumas parciales, insertando registros.
// ===========================================================================
module popcount_pipe #(
    parameter integer WIDTH  = 16384,
    parameter integer STAGES = 14
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire [WIDTH-1:0]    data_in,
    output reg  [13:0]         data_out
);

    // --- Comprobación de constantes ---
    generate if (WIDTH != 16384) $error("Popcount width must be 16384"); endgenerate

    // Declaración de arrays de pipeline:
    reg [13:0] stage_0 [0:8191];
    reg [13:0] stage_1 [0:4095];
    reg [13:0] stage_2 [0:2047];
    reg [13:0] stage_3 [0:1023];
    reg [13:0] stage_4 [0:511];
    reg [13:0] stage_5 [0:255];
    reg [13:0] stage_6 [0:127];
    reg [13:0] stage_7 [0:63];
    reg [13:0] stage_8 [0:31];
    reg [13:0] stage_9 [0:15];
    reg [13:0] stage_10[0:7];
    reg [13:0] stage_11[0:3];
    reg [13:0] stage_12[0:1];
    reg [13:0] stage_13[0:0]; // final

    // Implementación:
    integer i;

    // Etapa 0: Extraer pares de bits y formar números de 2 bits (realmente es de 2 bits)
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<8192; i=i+1) stage_0[i] <= 14'd0;
        end else begin
            for (i=0; i<8192; i=i+1)
                stage_0[i] <= {12'd0, data_in[2*i+1], data_in[2*i]}; // {2'd0, bits}
        end
    end

    // Etapa 1: Sumar pares de stage_0
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<4096; i=i+1) stage_1[i] <= 14'd0;
        end else begin
            for (i=0; i<4096; i=i+1)
                stage_1[i] <= stage_0[2*i] + stage_0[2*i+1];
        end
    end

    // Etapa 2
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<2048; i=i+1) stage_2[i] <= 14'd0;
        end else begin
            for (i=0; i<2048; i=i+1)
                stage_2[i] <= stage_1[2*i] + stage_1[2*i+1];
        end
    end

    // Etapa 3
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<1024; i=i+1) stage_3[i] <= 14'd0;
        end else begin
            for (i=0; i<1024; i=i+1)
                stage_3[i] <= stage_2[2*i] + stage_2[2*i+1];
        end
    end

    // Etapa 4
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<512; i=i+1) stage_4[i] <= 14'd0;
        end else begin
            for (i=0; i<512; i=i+1)
                stage_4[i] <= stage_3[2*i] + stage_3[2*i+1];
        end
    end

    // Etapa 5
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<256; i=i+1) stage_5[i] <= 14'd0;
        end else begin
            for (i=0; i<256; i=i+1)
                stage_5[i] <= stage_4[2*i] + stage_4[2*i+1];
        end
    end

    // Etapa 6
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<128; i=i+1) stage_6[i] <= 14'd0;
        end else begin
            for (i=0; i<128; i=i+1)
                stage_6[i] <= stage_5[2*i] + stage_5[2*i+1];
        end
    end

    // Etapa 7
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<64; i=i+1) stage_7[i] <= 14'd0;
        end else begin
            for (i=0; i<64; i=i+1)
                stage_7[i] <= stage_6[2*i] + stage_6[2*i+1];
        end
    end

    // Etapa 8
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<32; i=i+1) stage_8[i] <= 14'd0;
        end else begin
            for (i=0; i<32; i=i+1)
                stage_8[i] <= stage_7[2*i] + stage_7[2*i+1];
        end
    end

    // Etapa 9
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<16; i=i+1) stage_9[i] <= 14'd0;
        end else begin
            for (i=0; i<16; i=i+1)
                stage_9[i] <= stage_8[2*i] + stage_8[2*i+1];
        end
    end

    // Etapa 10
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<8; i=i+1) stage_10[i] <= 14'd0;
        end else begin
            for (i=0; i<8; i=i+1)
                stage_10[i] <= stage_9[2*i] + stage_9[2*i+1];
        end
    end

    // Etapa 11
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<4; i=i+1) stage_11[i] <= 14'd0;
        end else begin
            for (i=0; i<4; i=i+1)
                stage_11[i] <= stage_10[2*i] + stage_10[2*i+1];
        end
    end

    // Etapa 12
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i=0; i<2; i=i+1) stage_12[i] <= 14'd0;
        end else begin
            for (i=0; i<2; i=i+1)
                stage_12[i] <= stage_11[2*i] + stage_11[2*i+1];
        end
    end

    // Etapa 13 (final)
    always @(posedge clk) begin
        if (!rst_n) begin
            data_out <= 14'd0;
        end else begin
            data_out <= stage_12[0] + stage_12[1];
        end
    end

endmodule
