import random
import pygame
import sys
class Chip8:

    def __init__(self):
        self.keys = [0] * 16
        self.display = [0] * 32 * 64
        self.memory = [0] * 4096
        self.registers = [0] * 16
        self.sound_timer = 0
        self.delay_timer = 0
        self.index = 0
        self.draw_conditioner = False
        self.pc = 0x200
        self.stack = []


        # Init pygame and set the screen
        pygame.init();
        self.screen = pygame.display.set_mode([64 * 10, 32 * 10])


        # Opcode function map for indirect calling
        self.op_map = {
            0x0000: self._0nnn,
            0x00E0: self._00E0,
            0x00EE: self._00EE,
            0x1000: self._1nnn,
            0x2000: self._2nnn,
            0x3000: self._3xkk,
            0x4000: self._4xkk,
            0x5000: self._5xy0,
            0x6000: self._6xkk,
            0x7000: self._7xkk,
            0x8000: self._8nnn,
            0x8FF0: self._8xy0,
            0x8FF1: self._8xy1,
            0x8FF2: self._8xy2,
            0x8FF3: self._8xy3,
            0x8FF4: self._8xy4,
            0x8FF5: self._8xy5,
            0x8FF6: self._8xy6,
            0x8FF7: self._8xy7,
            0x8FFE: self._8xyE,
            0x9000: self._9xy0,
            0xA000: self._Annn,
            0xB000: self._Bnnn,
            0xC000: self._Cxkk,
            0xD000: self._Dxyn,
            0xE000: self._Ennn,
            0xE00E: self._Ex9E,
            0xE001: self._ExA1,
            0xF000: self._Fnnn,
            0xF007: self._Fx07,
            0xF00A: self._Fx0A,
            0xF015: self._Fx15,
            0xF018: self._Fx18,
            0xF01E: self._Fx1E,
            0xF029: self._Fx29,
            0xF033: self._Fx33,
            0xF055: self._Fx55,
            0xF065: self._Fx65
        }

        self.keyset = {
            pygame.K_1: 1,
            pygame.K_2: 2,
            pygame.K_3: 3,
            pygame.K_4: 12,
            pygame.K_q: 4,
            pygame.K_w: 5,
            pygame.K_e: 6,
            pygame.K_r: 13,
            pygame.K_a: 7,
            pygame.K_s: 8,
            pygame.K_d: 9,
            pygame.K_f: 14,
            pygame.K_z: 10,
            pygame.K_x: 0,
            pygame.K_b: 11,
            pygame.K_v: 15

        } 
        
        fonts = [ 
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        for i in range(len(fonts)):
            self.memory[i] = fonts[i]


    ''' loads the rom into memory '''
    def load_rom(self, rom):
        counter = 0 # counter used to calculate offset

        # open the file and read data into memory starting at pc 0x200
        with open(rom, 'rb') as file:
            data = file.read()
            for x in data:
                self.memory[counter + 0x200] = x
                counter += 1




    def execute_cycle(self):
        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1] # extracts the full 2 byte opcode
        
        print("Current opcode: ", hex(self.opcode))

        self.pc += 2
        self.op_map[self.opcode & 0xF000]()
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1

    def _0nnn(self):
        temp_op = self.opcode & 0xf0ff
        self.op_map[temp_op]()

    def _00E0(self):
        ''' clears the display'''
        self.display = [0] * 32 * 64
        
    def _00EE(self):
        ''' return from subroutine '''
        self.pc = self.stack.pop()
    
    def _1nnn(self):
        ''' sets pc to location specified by nnn '''
        self.pc = self.opcode & 0x0fff

    def _2nnn(self):
        ''' calls subroutine at nnn '''
        self.stack.append(self.pc)
        self.pc = self.opcode & 0x0fff
    
    def _3xkk(self):
        ''' skips next instruction if Vx == kk '''
        x = (self.opcode & 0x0f00) >> 8
        kk = self.opcode & 0x00ff
        if self.registers[x] == kk:
            self.pc += 2

    def _4xkk(self):
        ''' skips next instruction if Vx != kk '''
        x = (self.opcode & 0x0f00) >> 8
        kk = self.opcode & 0x00ff
        if self.registers[x] != kk:
            self.pc += 2

    def _5xy0(self):
        ''' skips next instruction if Vx == Vy '''
        x = (self.opcode & 0x0f00) >> 8
        y = (self.opcode & 0x00f0) >> 4
        if self.registers[x] == self.registers[y]:
            self.pc += 2

    def _6xkk(self):
        ''' set Vx == kk '''
        x = (self.opcode & 0x0f00) >> 8
        kk = self.opcode & 0xff
        self.registers[x] = kk 

    def _7xkk(self):
        ''' set Vx = Vx + kk '''
        x = (self.opcode & 0x0f00) >> 8
        kk = self.opcode & 0x00ff
        self.registers[x] += kk


    '''
    8000 Opcodes
    '''
    def _8nnn(self):
        temp_op = self.opcode & 0xf00f
        temp_op += 0xff0
        self.op_map[temp_op]()

    def _8xy0(self):
        ''' set Vx = Vy '''
        x = (self.opcode & 0x0f00) >> 8
        y = (self.opcode & 0x00f0) >> 4
        self.registers[x] = self.registers[y]
        self.registers[x] & 0x00ff
    
    def _8xy1(self):
        ''' set Vx = Vx | Vy '''
        x = (self.opcode & 0x0f00) >> 8
        y = (self.opcode & 0x00f0) >> 4
        self.registers[x] |= self.registers[y]
        self.registers[x] & 0x00ff

    def _8xy2(self):
        ''' set Vx = Vx & Vy '''
        x = (self.opcode & 0x0f00) >> 8
        y = (self.opcode & 0x00f0) >> 4
        self.registers[x] &= self.registers[y]
        self.registers[x] & 0x00ff

    def _8xy3(self):
        ''' set Vx = Vx ^ Vy '''
        x = (self.opcode & 0x0f00) >> 8
        y = (self.opcode & 0x00f0) >> 4
        self.registers[x] ^= self.registers[y]
        self.registers[x] & 0x00ff

    def _8xy4(self):
        ''' set Vx = Vx + Vy, set VF to the carry '''
        x = (self.opcode & 0x0f00) >> 8
        y = (self.opcode & 0x00f0) >> 4
        sum = self.registers[x] + self.registers[y]
        if sum > 0x00ff:
            self.registers[0xf] = 1
        else:
            self.registers[0xf] = 0 
        self.registers[x] = sum % 0x00ff 
        self.registers[x] & 0x00ff

    def _8xy5(self):
        ''' Vx = Vx - Vy, set Vf to NOT borrow '''
        x = (self.opcode & 0x0f00) >> 8
        y = (self.opcode & 0x00f0) >> 4
        if self.registers[x] > self.registers[y]:
            self.registers[0xf] = 1
        else: 
            self.registers[0xf] = 0
        self.registers[x] -= self.registers[y] 
        self.registers[x] & 0x00ff

    def _8xy6(self):
        ''' Vx = Vx SHR 1 '''
        x = (self.opcode & 0x0f00) >> 8
        self.registers[0xf] = (self.registers[x] & 0x0001)
        self.registers[x] >>= 1
    
    def _8xy7(self):
        ''' Vx = Vy - Vx, set VF = not borrow '''
        x = (self.opcode & 0x0f00) >> 8
        y = (self.opcode & 0x00f0) >> 4
        if self.registers[y] > self.registers[x]:
            self.registers[0xf] = 1
        else: 
            self.registers[0xf] = 0
        self.registers[x] = self.registers[y] - self.registers[x]
        self.registers[x] & 0x00ff

    def _8xyE(self):
        ''' Vx = Vx SHL 1 '''
        x = (self.opcode & 0x0f00) >> 8
        self.registers[0xf] = (self.registers[x] & 0x80) >> 7
        self.registers[x] <<= 1
        self.registers[x] & 0x00ff
    
    def _9xy0(self):
        ''' skip next instruction if Vx != Vy '''
        x = (self.opcode & 0x0f00) >> 8
        y = (self.opcode & 0x00f0) >> 4
        if self.registers[x] != self.registers[y]:
            self.pc += 2

    def _Annn(self):
        ''' set register I to nnn '''
        self.index = (self.opcode & 0x0fff)
    
    def _Bnnn(self):
        ''' pc is set to nnn + V0 '''
        self.pc = (self.opcode & 0x0fff) + self.registers[0]

    def _Cxkk(self):
        ''' Vx = random num AND kk '''
        x = (self.opcode & 0x0f00) >> 8
        kk = (self.opcode & 0x00ff)
        randNum = int(random.random() * 0xff)
        self.registers[x] = randNum & kk 
        self.registers[x] & 0x00ff

    def _Dxyn(self):
        vx = (self.opcode & 0x0f00) >> 8
        vy = (self.opcode & 0x00f0) >> 4 

        x = self.registers[vx] 
        y = self.registers[vy] 

        height = self.opcode & 0x000F
        self.registers[0xF] = 0

        for row in range(height):
            pxByte = self.memory[int(self.index) + row]
            for offSet in range(8):
                if ((y + row < 32)) and ((x + offSet - 1) < 64):
                    if(pxByte & (0x80 >> offSet)) != 0:
                        if self.display[(x + offSet + ((y + row) * 64))] == 1:
                            self.registers[0xF] = 1
                        self.display[(x + offSet + ((y + row) * 64))] ^= 1

        self.draw_conditioner = True

    def _Ennn(self):
        temp_op = self.opcode & 0xf00f
        self.op_map[temp_op]()

    def _Ex9E(self):
        ''' skip next instruction if key of value Vx is pressed '''
        x = (self.opcode & 0x0f00) >> 8
        if self.keys[self.registers[x]]:
            self.pc += 2;

    def _ExA1(self):
        ''' skip next instruction if key of value Vx is not pressed '''
        x = (self.opcode & 0x0f00) >> 8
        if not self.keys[self.registers[x]]:
            self.pc += 2;

    def _Fnnn(self):
        temp_op = self.opcode & 0xf0ff
        self.op_map[temp_op]()  

    def _Fx07(self):
        ''' set Vx = delay timer '''
        x = (self.opcode & 0x0f00) >> 8
        self.registers[x] = self.delay_timer 

    def _Fx0A(self):
        ''' wait for a keypress, store the value in Vx '''
        x = (self.opcode & 0x0f00) >> 8
        hasPressed = False;
        for i in range(len(self.keys)):
            if self.keys[i]:
                self.registers[x] = i
                hasPressed = True
                break
        if not hasPressed:
            self.pc -= 2

    def _Fx15(self):
        ''' set delay timer = Vx '''
        x = (self.opcode & 0x0f00) >> 8
        self.delay_timer = self.registers[x]

    def _Fx18(self):
        ''' set sound timer = Vx '''
        x = (self.opcode & 0x0f00) >> 8
        self.sound_timer = self.registers[x]

    def _Fx1E(self):
        ''' set index = index + Vx '''
        x = (self.opcode & 0x0f00) >> 8
        self.index += self.registers[x]

    def _Fx29(self):
        ''' set index to location of sprite for digit Vx '''
        x = (self.opcode & 0x0f00) >> 8
        self.index = self.registers[x] * 5

    def _Fx33(self):
        ''' store BCD rep of Vx in memory locations I, I+1, I+2'''
        x = (self.opcode & 0x0f00) >> 8
        self.memory[self.index + 2] = self.registers[x] % 10;
        self.memory[self.index + 1] = (self.registers[x] / 10) % 10;
        self.memory[self.index] = self.registers[x] % 100;

    def _Fx55(self):
        ''' Store registers V0 - Vx in memory starting at index '''
        x = (self.opcode & 0x0f00) >> 8
        for reg in range(0, x + 1):
            self.memory[self.index + reg] = self.registers[reg];

    def _Fx65(self):
        ''' Read registers V0 - Vx from memory starting at I '''
        x = (self.opcode & 0x0f00) >> 8
        for i in range(0, x + 1):
            self.registers[i] = self.memory[self.index + i]

    def render(self):
        for y in range(32):
            for x in range(64):
                cellColor = [0, 0, 50]

                if self.display[y * 64 + x ] == 1:
                    cellColor = [255, 255, 255] 
                pygame.draw

        
            
                pygame.draw.rect(self.screen, cellColor, [y * 10, x * 10, 10, 10], 0)
        pygame.display.flip()



chip8 = Chip8()
chip8.load_rom("./Roms/test_opcode.ch8")
clock = pygame.time.Clock()
quit = False

while not quit:
    chip8.execute_cycle()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            chip8.keys[chip8.keyset[event.key]] = True;
        elif event.type == pygame.KEYUP:
            chip8.keys[chip8.keyset[event.key]] = False; 
        
    if chip8.draw_conditioner:
        chip8.draw_conditioner = False
        for y in range(32):
            for x in range(64):
                if chip8.display[x + (y*64)] == 0:
                    pygame.draw.rect(chip8.screen, (0,0,0), (x*10,y*10,10,10), 0)
                else:
                    pygame.draw.rect(chip8.screen, (255,255,255), (x*10,y*10,10,10), 0)
    pygame.display.flip()
