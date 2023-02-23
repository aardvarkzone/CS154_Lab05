import pyrtl

# ucsbcs154lab5
# All Rights Reserved
# Copyright (c) 2023 Regents of the University of California
# Distribution Prohibited

#ADD, AND, ADDI, LUI, ORI, SLT, LW, SW, BEQ

# Initialize your memblocks here: 
i_mem = pyrtl.MemBlock(bitwidth=32, addrwidth=32, 
                    name='i_mem')
d_mem = pyrtl.MemBlock(bitwidth=32, addrwidth=32, max_read_ports=2, max_write_ports=1,
                    name='d_mem', asynchronous=True)
rf = pyrtl.MemBlock(bitwidth=32, addrwidth=32, max_read_ports=2, max_write_ports=1,
                    name='rf', asynchronous=True, )


#wirevectors / registers 
instr = pyrtl.WireVector(bitwidth=32, name='instr')
alu_out = pyrtl.WireVector(bitwidth=32, name='alu_out')
op = pyrtl.WireVector(bitwidth=6, name='op')
rs = pyrtl.WireVector(bitwidth=5, name='rs')
rt = pyrtl.WireVector(bitwidth=5, name='rt')
rd = pyrtl.WireVector(bitwidth=5, name='rd')
sh = pyrtl.WireVector(bitwidth=5, name='sh')
func = pyrtl.WireVector(bitwidth=6, name='func')
imm = pyrtl.WireVector(bitwidth=16, name='imm')
addr = pyrtl.WireVector(bitwidth=26, name='addr')
data0 = pyrtl.WireVector(bitwidth=32, name='data 0')
data1 = pyrtl.WireVector(bitwidth=32, name='data 1')
temp1 = pyrtl.WireVector(bitwidth=32, name='temp 1')
pc = pyrtl.Register(bitwidth=32, name='program counter', reset_value=0)
control = pyrtl.WireVector(bitwidth=10, name='control')
reg_dst = pyrtl.WireVector(bitwidth=1, name='reg_dst')
branch = pyrtl.WireVector(bitwidth=1, name='branch')
reg_write = pyrtl.WireVector(bitwidth=1, name='reg_write')
alu_src = pyrtl.WireVector(bitwidth=2, name='alu_src')
mem_write = pyrtl.WireVector(bitwidth=1, name='mem_write')
mem_to_reg = pyrtl.WireVector(bitwidth=1, name='mem_to_reg')
alu_op = pyrtl.WireVector(bitwidth=3, name='alu_op')

instr <<= i_mem[pc]


# When working on large designs, such as this CPU implementation, it is
# useful to partition your design into smaller, reusable, hardware
# blocks. In PyRTL, one way to do this is through functions. Here are 
# some examples of hardware blocks that can help you get started on this
# CPU design. You may have already worked on this logic in prior labs.

def ucsbcs154lab5_decode():
   global instr, alu_out, op, rs, rt, rd, sh, func, imm
   global addr, data0, data1, temp1, pc, control, i_mem, d_mem, rf
   global reg_dst, branch, reg_write, alu_src, mem_write, mem_to_reg, alu_op
   op <<= instr[26:32]
   rs <<= instr[21:26]
   rt <<= instr[16:21]
   rd <<= instr[11:16]
   sh <<= instr[6:11]
   func <<= instr[0:6]
   imm <<= instr[0:16]
   addr <<= instr[0:26]
   

def ucsbcs154lab5_alu():
   # take data 0, data 1 and lab 4 
   global instr, alu_out, op, rs, rt, rd, sh, func, imm
   global addr, data0, data1, temp1, pc, control, i_mem, d_mem, rf
   global reg_dst, branch, reg_write, alu_src, mem_write, mem_to_reg, alu_op
   with pyrtl.conditional_assignment: 
      with (alu_op == 0b000): #add
         alu_out |= (data0 + data1)
      with (alu_op == 0b001): #and 
         alu_out |= (data0 & data1)
      with (alu_op == 0b010): #lui
         #alu_out |= pyrtl.concat(data0, 0b0000000000000000)
         alu_out |= pyrtl.shift_left_logical(data1, pyrtl.Const(16)) 
      with (alu_op == 0b011): #or
         alu_out |= (data0 | data1)
      with (alu_op == 0b100): #slt
         alu_out |= pyrtl.signed_lt(data0, data1) 
      with (alu_op == 0b101): #sub 
         alu_out |= (data0 - data1)


def ucsbcs154lab5_controller():
   global instr, alu_out, op, rs, rt, rd, sh, func, imm
   global addr, data0, data1, temp1, pc, control, i_mem, d_mem, rf
   global reg_dst, branch, reg_write, alu_src, mem_write, mem_to_reg, alu_op
   with pyrtl.conditional_assignment:
      with (op == 0b000000): 
         #R-Types
         with (func == 0b100000):
            #ADD
            control |= 0b1010000000
         with (func == 0b100100):
            #AND
            control |= 0b1010000001
         with (func == 0b101010):
            #SLT
            control |= 0b1010000100
      with (op == 0b001000): 
         #ADDI
         control |= 0b0010100000
      with (op == 0b001111):
         #LUI
         control |= 0b0010100010
      with (op == 0b001101): 
         #ORI
         control |= 0b0011000011
      with (op == 0b100011): 
         #LW
         control |= 0b0010101000
      with (op == 0b101011): 
         #SW
         control |= 0b0000110000
      with (op == 0b000100): 
         #BEQ
         control |= 0b0100000101

   alu_op <<= control[0:3]
   mem_to_reg <<= control[3]
   mem_write <<= control[4]
   alu_src <<= control[5:7]
   reg_write <<= control[7]
   branch <<= control[8]
   reg_dst <<= control[9]

def ucsbcs154lab5_reg_read():
   # use control signal to figure out read from mem / registers 
   # set data 0 / data 1
   # two values from reg file

   global instr, alu_out, op, rs, rt, rd, sh, func, imm
   global addr, data0, data1, temp1, pc, control, i_mem, d_mem, rf
   global reg_dst, branch, reg_write, alu_src, mem_write, mem_to_reg, alu_op
   data0 <<= rf[rs]
   temp1 <<= rf[rt]
   with pyrtl.conditional_assignment:
      with alu_src == 0b00:
         data1 |= temp1 
      with alu_src == 0b01:
         data1 |= imm.sign_extended(32)
         #data1 should taken $t3
      with alu_src == 0b10:
         data1 |= imm.zero_extended(32)

def ucsbcs154lab5pc_update():
   global instr, alu_out, op, rs, rt, rd, sh, func, imm
   global addr, data0, data1, temp1, pc, control, i_mem, d_mem, rf
   global reg_dst, branch, reg_write, alu_src, mem_write, mem_to_reg, alu_op
   with pyrtl.conditional_assignment:
      with (branch == 0):
         pc.next |= pc + 1
      with (branch == 1):
         with (alu_out == 0):
            pc.next |= pc + 1 + imm.sign_extended(32)
         with pyrtl.otherwise:
            pc.next |= pc + 1
   #in branch, increment with address 

def ucsbcs154lab5_write_back():
   # figure out what to write to using control 
   # rt, rd, memory, etc. 
   # check for 0 reg 
   global instr, alu_out, op, rs, rt, rd, sh, func, imm
   global addr, data0, data1, temp1, pc, control, i_mem, d_mem, rf
   global reg_dst, branch, reg_write, alu_src, mem_write, mem_to_reg, alu_op
   with pyrtl.conditional_assignment:
      with (reg_write == 1): 
         # regwrite = 1
         with (mem_to_reg == 1):
            # memtoreg = 1 --> lw --> rf[rt]
            with (rt != 0): 
               rf[rt] |= d_mem[alu_out]
         with (mem_to_reg == 0):
            # memtoreg = 0
            with (reg_dst == 1):
               # regdst = 1 --> rf[rd]
               with (rd != 0): 
                  rf[rd] |= alu_out
            with (reg_dst == 0):
               # regdst = 0 --> rf[rt]
               with (rt != 0): 
                  rf[rt] |= alu_out
      with (reg_write == 0):
         with (mem_write == 1):
            d_mem[alu_out] |= temp1
          

# These functions implement smaller portions of the CPU design. A 
# top-level function is required to bring these smaller portions
# together and finish your CPU design. Here you will instantiate 
# the functions, i.e., build hardware, and orchestrate the various 
# parts of the CPU together. 

def ucsbcs154lab5_top():
   global instr, alu_out, op, rs, rt, rd, sh, func, imm
   global addr, data0, data1, temp1, pc, control, i_mem, d_mem, rf
   global reg_dst, branch, reg_write, alu_src, mem_write, mem_to_reg, alu_op
   ucsbcs154lab5_decode()
   ucsbcs154lab5_controller()
   ucsbcs154lab5_reg_read()
   ucsbcs154lab5_alu()
   ucsbcs154lab5_write_back()
   ucsbcs154lab5pc_update()

ucsbcs154lab5_top()

if __name__ == '__main__':

    """

    Here is how you can test your code.
    This is very similar to how the autograder will test your code too.

    1. Write a MIPS program. It can do anything as long as it tests the
       instructions you want to test.

    2. Assemble your MIPS program to convert it to machine code. Save
       this machine code to the "i_mem_init.txt" file.
       You do NOT want to use QtSPIM for this because QtSPIM sometimes
       assembles with errors. One assembler you can use is the following:

       https://alanhogan.com/asu/assembler.php

    3. Initialize your i_mem (instruction memory).

    4. Run your simulation for N cycles. Your program may run for an unknown
       number of cycles, so you may want to pick a large number for N so you
       can be sure that the program so that all instructions are executed.

    5. Test the values in the register file and memory to make sure they are
       what you expect them to be.

    6. (Optional) Debug. If your code didn't produce the values you thought
       they should, then you may want to call sim.render_trace() on a small
       number of cycles to see what's wrong. You can also inspect the memory
       and register file after every cycle if you wish.

    Some debugging tips:

        - Make sure your assembly program does what you think it does! You
          might want to run it in a simulator somewhere else (SPIM, etc)
          before debugging your PyRTL code.

        - Test incrementally. If your code doesn't work on the first try,
          test each instruction one at a time.

        - Make use of the render_trace() functionality. You can use this to
          print all named wires and registers, which is extremely helpful
          for knowing when values are wrong.

        - Test only a few cycles at a time. This way, you don't have a huge
          500 cycle trace to go through!

    """

    # Start a simulation trace
    sim_trace = pyrtl.SimulationTrace()

    # Initialize the i_mem with your instructions.
    i_mem_init = {}
    with open('i_mem_init.txt', 'r') as fin:
        i = 0
        for line in fin.readlines():
            i_mem_init[i] = int(line, 16)
            i += 1

    sim = pyrtl.Simulation(tracer=sim_trace, memory_value_map={
        i_mem : i_mem_init
    })

    # Run for an arbitrarily large number of cycles.
    for cycle in range(500):
        sim.step({})
        print(sim.inspect_mem(rf))


    # Use render_trace() to debug if your code doesn't work.
    sim_trace.render_trace()

    # You can also print out the register file or memory like so if you want to debug:
    print(sim.inspect_mem(d_mem))
    print(sim.inspect_mem(rf))

    # Perform some sanity checks to see if your program worked correctly
    #assert(sim.inspect_mem(d_mem)[0] == 10)
    #assert(sim.inspect_mem(rf)[8] == 10)    # $v0 = rf[8]

    #print('Passed!')
   #tests taken from piazza user Kevin Lavelle
   #Test 1
   # test addi max 32 bit number to $t0, store in $t0
    assert(sim.inspect_mem(rf)[8] == 0xFFFFFFFF), 'Error in Test 1, MIPS Program Line 1, incorrect ADDI result'
    #Test 2
    #test add max 32 bit number to $t1 using $t0 and $zero, store in $t1
    assert(sim.inspect_mem(rf)[9] == 0xFFFFFFFF), 'Error in Test 2, MIPS Program Line 2, incorrect ADD result'
    #Test 3
    #test addi max 32 bit number to 0xFFFF to produce overflow, store in $k0
    assert(sim.inspect_mem(rf)[26] == 0xFFFFFFFE), 'Error in Test 3, MIPS Program Line 3, incorrect ADDI result with overflow'
    #Test 4 
    #test add max 32 bit number to another max 32 bit number to produce overflow, store in $k1
    assert(sim.inspect_mem(rf)[27] == 0xFFFFFFFE), 'Error in Test 4, MIPS Program Line 4, incorrect ADD result with overflow'
    #Test 5 
    #test LUI on max 16-bit immediate, store in $t2
    assert(sim.inspect_mem(rf)[10] == 0xFFFF0000), 'Error in Test 5, MIPS Program Line 5, incorrect LUI result'
    #Test 6 
    #test LUI on non-zero 16-bit intermediate, store in $t3
    assert(sim.inspect_mem(rf)[11] == 0x00010000), 'Error in Test 6, MIPS Program Line 6, incorrect LUI result'
    #Test 7 
    #test LUI on zero, store in $t4
    assert(sim.inspect_mem(rf)[12] == 0x00000000), 'Error in Test 7, MIPS Program Line 7, incorrect LUI result'
    #Test 8 
    #test ORI on register with $t0 (0xFFFFFFFF) and 0x0, store in $t5``
    assert(sim.inspect_mem(rf)[13] == 0xFFFFFFFF), 'Error in Test 8, MIPS Program Line 8, incorrect ORI result'
    #Test 9
    #test ORI on $t3 (0x00010000) and a random immediate (0xF069), store in $t6
    assert(sim.inspect_mem(rf)[14] == 0x1F069), 'Error in Test 9, MIPS Program Line 9, incorrect ORI result '
    #Test 10 
    #test slt on two non-negative numbers, $t4 < $t3, store in $s0
    assert(sim.inspect_mem(rf)[16] == 1), 'Error in Test 10, MIPS Program Line 10, incorrect slt result with two non-negatives'
    #Test 11
    #reverse of Test 10, test slt on two non-negative numbers, $t3 > $t4, store $s1
    assert(sim.inspect_mem(rf)[17] == 0), 'Error in Test 11, MIPS Program Line 11, incorrect slt result with two non-negatives'
    #Test 12 
    #test slt on two negative numbers, $k1 < $t0, store in $s2
    assert(sim.inspect_mem(rf)[18] == 1), 'Error in Test 12, MIPS Program Line 12, incorrect slt result with two negatives'
    #Test 13 
    #test slt on two negative numbers, $t0 < $k1, store in $s3
    assert(sim.inspect_mem(rf)[19] == 0), 'Error in Test 13, MIPS Program Line 13, incorrect slt result with two negatives'
    #Test 14 
    #test slt on a negative and positive number, $t0 < $t3, store in $s4
    assert(sim.inspect_mem(rf)[20] == 1), 'Error in Test 14, MIPS Program Line 14, incorrect slt results with negative < positive'
    #Test 15
    #reverse of Test 14, test slt on a negative and positive number, $t3 > $t0, store in $s5
    assert(sim.inspect_mem(rf)[21] == 0), 'Error in Test 15, MIPS Program Line 15, incorrect slt results with positive > negative'
    #Test 16 
    #test slt on two positive numbers that are equal, store in $s6
    assert(sim.inspect_mem(rf)[22] == 0), 'Error in Test 16, MIPS Program Line 16, incorrect slt result of two positives'
    #Test 17
    #test slt on two negative numbers that are equal, store in $s7
    assert(sim.inspect_mem(rf)[23] == 0), 'Error in Test 17, MIPS Program Line 17, incorrect slt result of two negatives'
    #Test 18 
    #test slt on comparison between zero and zero, store in $t7
    assert(sim.inspect_mem(rf)[15] == 0), 'Error in Test 18, MIPS Program Line 18, incorrect slt result of zero and zero'
    #Test 19
    #ensure BEQ works on an immediate of zero
    assert(sim.inspect_mem(rf)[4] == 5), 'Error in Test 19, MIPS Program Lines 19-20, likely line 19, incorrect BEQ jump with immediate of zero'
    #Test 20
    #test BEQ for correct jump of lines
    assert(sim.inspect_mem(rf)[5] == 3), 'Error in Test 20, MIPS Program Lines 21-24, likely line 21, incorrect BEQ line jumping'
    #Test 21
    #ensure BEQ does not break on not equal values
    assert(sim.inspect_mem(rf)[6] == 5), 'Error in Test 21, MIPS Program Lines 25-27, likely line 26, BEQ should not break here'
    #Test 22
    #test sw with an immediate of zero
    assert(sim.inspect_mem(d_mem)[0] == 0x1F069), 'Error in Test 22, MIPS Program Line 28, SW with immediate of zero'
    #Test 23
    #test sw with a positive immediate
    assert(sim.inspect_mem(d_mem)[3] == 0x1F069), 'Error in Test 23, MIPS Program Line 29, SW with positive immediate'
    #Test 24
    #test sw with a positive immediate and a nonzero address
    assert(sim.inspect_mem(d_mem)[6] == 0x1F069), 'Error in Test 24, MIPS Program Line 30, SW with positive immediate and nonzero address'
    #Test 25
    #test sw with a negative immediate and a nonzero address
    assert(sim.inspect_mem(d_mem)[2] == 0x1F069), 'Error in Test 25, MIPS Program Line 31, SW with negative immediate'
    #Test 26
    #test and with $t5 (0xFFFFFFFF) and $t6 (0x1F069), store in $a3
    assert(sim.inspect_mem(rf)[7] == 0x1F069), 'Error in Test 26, MIPS Program Line 32, AND with $t5 and $t6'
   #Test 27
   #test and with $t4 (0x0) and $t5 (0xFFFFFFFF), store in $at
    assert(sim.inspect_mem(rf)[1] == 0), 'Error in Test 27, MIPS Program Line 33, AND with 0x0 and 0xFFFFFFFF'
    #Test 28
    #test lw with an immediate of zero, load word into $gp from $a1 (3)
    assert(sim.inspect_mem(rf)[28] == 127081), 'Error in Test 28, MIPS Program Line 34, LW with immediate of zero'
    #Test 29 
    #test lw with a positive immediate (2), load word into $sp from $a1 plus the immediate (3+3=6)
    assert(sim.inspect_mem(rf)[29] == 127081), 'Error in Test 29, MIPS Program Line 35, LW with positive immediate'
    #Test 30
    #test lw with a negative immediate (-3), load word into $fp from $a1 plus the immediate (3-3=0)
    assert(sim.inspect_mem(rf)[30] == 127081), 'Error in Test 30, MIPS Program Line 36, LW with negative immediate'
    #Test 31
    #Make sure that the zero register (rf[0) is never modified in the program
    assert(0 not in sim.inspect_mem(rf).keys()), 'Error in Test 31, MIPS Program Lines 37-43, NO FUNCTION SHOULD MODIFY the $zero register'
    #Test 32
    #More complicated loop program
    #Iterate a memory value until it BEQs
    #Similar to given program on Canvas files
    assert(sim.inspect_mem(d_mem)[15] == 10), 'Error in Test 32, MIPS Program Lines 44-52, code is from loop on Canvas'


    print('Passed!')





