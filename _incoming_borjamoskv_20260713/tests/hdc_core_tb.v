`timescale 1ns / 1ps

module hdc_core_tb;

    // Parametros
    parameter D = 16384;
    parameter CODEBOOK_DEPTH = 16; // Test corto
    parameter POPCOUNT_STAGES = 14;
    parameter ADDR_WIDTH = $clog2(CODEBOOK_DEPTH);

    // Señales
    reg clk;
    reg rst_n;
    reg start;
    reg [D-1:0] query;
    wire done;
    wire [ADDR_WIDTH-1:0] match_idx;
    wire [13:0] match_dist;

    wire codebook_rd_en;
    wire [ADDR_WIDTH-1:0] codebook_rd_addr;
    reg [D-1:0] codebook_rd_data;

    // Memoria simulada
    reg [D-1:0] sram [0:CODEBOOK_DEPTH-1];

    // Instancia del HDC core
    hdc_core #(
        .D(D),
        .CODEBOOK_DEPTH(CODEBOOK_DEPTH),
        .POPCOUNT_STAGES(POPCOUNT_STAGES),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .query(query),
        .done(done),
        .match_idx(match_idx),
        .match_dist(match_dist),
        .codebook_rd_en(codebook_rd_en),
        .codebook_rd_addr(codebook_rd_addr),
        .codebook_rd_data(codebook_rd_data)
    );

    // Reloj
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Modelo de SRAM Síncrona
    always @(posedge clk) begin
        if (codebook_rd_en) begin
            codebook_rd_data <= sram[codebook_rd_addr];
        end
    end

    integer i;

    // Generador de estímulos
    initial begin
        // Inicializar SRAM
        for (i = 0; i < CODEBOOK_DEPTH; i = i + 1) begin
            sram[i] = {D{1'b1}}; // Todo a 1 (dist = 16384)
        end
        // Insertar algunos patrones
        // Vector 0: distancia = D (invirtiendo todo)
        sram[0] = {D{1'b1}}; 
        // Vector 5: distancia = 0 (igual al query)
        sram[5] = {D{1'b0}};
        // Vector 10: distancia = 5 (5 bits diferentes)
        sram[10] = {D{1'b0}};
        sram[10][4:0] = 5'b11111;
        // Vector 15 (fin): distancia = 1 (1 bit diferente)
        sram[15] = {D{1'b0}};
        sram[15][0] = 1'b1;

        // Reset
        rst_n = 0;
        start = 0;
        query = {D{1'b0}}; // Query todo a 0
        #20;
        rst_n = 1;
        #10;

        // Iniciar búsqueda
        $display("[%0t] Starting associative search...", $time);
        start = 1;
        #10;
        start = 0;

        // Esperar a que termine
        wait(done == 1'b1);
        $display("[%0t] Search done!", $time);
        $display("Match Index: %d", match_idx);
        $display("Match Distance: %d", match_dist);

        // Verificar resultados
        // El menor debe ser el vector 5 (distancia 0)
        if (match_idx == 5 && match_dist == 0) begin
            $display("TEST PASSED: Correct match found (idx 5, dist 0).");
        end else begin
            $display("TEST FAILED: Expected idx 5, dist 0. Got idx %d, dist %d", match_idx, match_dist);
        end

        // Finalizar
        #50;
        $finish;
    end

    // Opcional: Volcar a VCD
    initial begin
        $dumpfile("hdc_core.vcd");
        $dumpvars(0, hdc_core_tb);
    end

endmodule
