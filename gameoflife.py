#Conway's Game of Life (Pygame Edition)
#Will Sieber, Tyler Trevillian, Giovanni Rodriguez
#+ Lots of help from Stack Overflow, Pygame docs, & various example programs


#      ~Hotkeys~
#    G   - grid on/off
#    S   - screenshot
#    O   - settings
#  Space - pause/play


#########################INIT
import sys, time, pygame, tkinter, pygame_gui

pygame.init()
pygame.display.set_caption("Conway's Game of Life: Paused")
pygame.mouse.set_cursor(*pygame.cursors.broken_x)

icon = pygame.image.load("gameoflifeproj/files/icon.ico")
pygame.display.set_icon(icon)

#Load settings from file
cfg = []

with open("gameoflifeproj/files/options.cfg", "r") as config:
    for line in config:
        cfg.append(line)

CELL_SIZE  =      int(cfg[0])
SPEED_CELL =      int(cfg[1])
GRID_STATE = bool(int(cfg[2]))
SCREEN_VAL =      int(cfg[3])

WHITE = [255,255,255]
GRAY  = [230,230,230]
BLACK = [0,0,0]

#Init window/UI & variables
width, height = 1200, 700
blockS = CELL_SIZE
speed  = SPEED_CELL
size   = width - (width%blockS), height - (height%blockS) + 100

manager = pygame_gui.UIManager(size)
UI = pygame.Surface(size)
window_surface = pygame.Surface(size)

start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((width-(width%blockS)-130, height-(height%blockS)+20), (100, 30)), text='Start/Stop', manager=manager)
step_button  = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((width-(width%blockS)-120, height-(height%blockS)+50), (80, 30)), text='Step', manager=manager)
cfg_button   = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((width-(width%blockS)-210, height-(height%blockS)+35), (75, 30)), text='Options', manager=manager)
scre_button  = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((width-(width%blockS)-310, height-(height%blockS)+35), (95, 30)), text='Screenshot', manager=manager)

screen = pygame.display.set_mode(size)
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("Verdana", 20)

#Use list comprehension
arrX = width//blockS
arrY = height//blockS
block     = [[False]*arrX for i in range(arrY)]
nextBlock = [[False]*arrX for i in range(arrY)]

########################CLASS
#https://stackoverflow.com/questions/2395431/using-tkinter-in-python-to-edit-the-title-bar
#https://stackoverflow.com/questions/21958534/how-can-i-prevent-a-window-from-being-resized-with-tkinter

class Window:
    
    def __init__(self):
        self.main_window = tkinter.Tk()
        self.frame = tkinter.Frame()
    
    #Init options window (when called)
    def options(self):
        self.main_window.iconbitmap('gameoflifeproj/files/icon.ico')
        self.main_window.title("Conway's Game of Life: Options")
        self.main_window.geometry("{}x{}".format(400, 180))
        self.main_window.resizable(width=False, height=False)
        
        self.prompt_label = tkinter.Label(self.frame, text='Change Cell Size:')
        self.prompt_label.pack()
        self.gridEntry = tkinter.Entry(self.frame, width=10)
        self.gridEntry.insert(0, str(CELL_SIZE))
        self.gridEntry.pack()
        
        self.prompt_label = tkinter.Label(self.frame, text='Change Speed (Lower is Faster):')
        self.prompt_label.pack()
        self.speedEntry = tkinter.Entry(self.frame, width=10)
        self.speedEntry.insert(0, str(SPEED_CELL))
        self.speedEntry.pack()
        
        self.prompt_label = tkinter.Label(self.frame, text='')
        self.prompt_label.pack()
        
        self.calc_button = tkinter.Button(self.frame, text='Save', command=self.changeOptions)
        self.calc_button.pack()
    
        self.frame.pack()
        tkinter.mainloop()
        
    #Write to option file when save is pressed
    def changeOptions(self):
        
        if str(self.gridEntry.get()) != "" and str(self.speedEntry.get()) != "":
            with open("gameoflifeproj/files/options.cfg", "w") as optionFile:
                optionFile.write(str(self.gridEntry.get()) + '\n')
                optionFile.write(str(self.speedEntry.get()) + '\n')
                optionFile.write(str(cfg[2]))
                optionFile.write(str(cfg[3]))
                
            print("Changes saved... restart program to apply")
            time.sleep(1)
            self.main_window.destroy()
            sys.exit()
        
        else:
            print("Values must be input for each box")

#########################LOOP

def main():

    acc           = 0
    generation    = 0
    running       = False
    screenshotNum = SCREEN_VAL
    grid          = GRID_STATE
    
    while True:
        #Set screen color to white, acc variable
        acc += 1
        screen.fill(WHITE)
            
        run(drawCells)
        if grid:
            run(drawGrid)
        
        #Check when to apply rules
        if acc%speed == 0 and running:
            run(checkSurrounding)
            run(updateBlock)
            generation += 1
            acc = 0
            
        #Update screen/UI
        screen.blit(updateText(generation), (2, height - 2))
        
        manager.update(clock.tick())
        window_surface.blit(UI, (0, 0))
        manager.draw_ui(screen)
        
        pygame.display.update()
        
        #Check for events (quit, placeBlocks, start/stop)
        for event in pygame.event.get():
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                run(placeCells)
                
            if event.type == pygame.QUIT:
                
                #When exiting, save screenshot value
                with open("gameoflifeproj/files/options.cfg", "w") as optionFile:
                    optionFile.write(str(cfg[0]))
                    optionFile.write(str(cfg[1]))
                    optionFile.write(str(cfg[2]))
                    optionFile.write(str(screenshotNum))
                
                sys.exit()
            
            #Check for GUI events
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_button:
                        if running:
                            print('Paused!')
                            pygame.display.set_caption("Conway's Game of Life: Paused")
                            running = False
                        else:
                            print('Running...')
                            pygame.display.set_caption("Conway's Game of Life: Running")
                            running = True
                            
                    if event.ui_element == step_button and not running:
                        run(checkSurrounding)
                        run(updateBlock)
                        generation += 1
                        
                    if event.ui_element == cfg_button:
                        running = False
                        pygame.display.set_caption("Conway's Game of Life: Paused")
                        runOption = Window()
                        runOption.options()
                        
                    if event.ui_element == scre_button:
                        rect = pygame.Rect(0, 0, width - (width%blockS), height - (height%blockS))
                        sub = screen.subsurface(rect)
                        pygame.image.save(sub, "gameoflifeproj/files/screenshots/screenshot{0}.jpg".format(screenshotNum))
                        print("Screenshot saved!")
                        screenshotNum = screenshotNum + 1
            
            #Necessary for PygameGUI
            manager.process_events(event)
            
            #https://stackoverflow.com/questions/16044229/how-to-get-keyboard-input-in-pygame
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_SPACE:
                    if running:
                        pygame.display.set_caption("Conway's Game of Life: Paused")
                        running = False
                    else:
                        pygame.display.set_caption("Conway's Game of Life: Running")
                        running = True
                        
                if event.key == pygame.K_g:
                    grid = not grid
                        
                if event.key == pygame.K_o:
                    running = False
                    pygame.display.set_caption("Conway's Game of Life: Paused")
                    runOption = Window()
                    runOption.options()
                
                #https://stackoverflow.com/questions/17267395/how-to-take-screenshot-of-certain-part-of-screen-in-pygame
                if event.key == pygame.K_s:
                    rect = pygame.Rect(0, 0, width - (width%blockS), height - (height%blockS))
                    sub = screen.subsurface(rect)
                    pygame.image.save(sub, "gameoflifeproj/files/screenshots/screenshot{0}.jpg".format(screenshotNum))
                    print("Screenshot saved!")
                    screenshotNum = screenshotNum + 1
                    

####################FUNCTIONS

#Iterates through list for each function
def run(func):
    for y in range(len(block)):
        for x in range(len(block[y])):
            func(x,y,block)

#Find mouse pos and check each cell (https://stackoverflow.com/questions/12150957)
def placeCells(x,y,block):
    pos = pygame.mouse.get_pos()
    cell = pygame.Rect(x*blockS, y*blockS, blockS, blockS)
    if cell.collidepoint(pos) == 1:
        block[y][x] = not block[y][x]

#Draw cells to screen
def drawCells(x,y,block):
    if block[y][x]:
        cell = pygame.Rect(x*blockS, y*blockS, blockS, blockS)
        pygame.draw.rect(screen, BLACK, cell, 0)
        
#Draw grid to screen (https://stackoverflow.com/questions/41189928)
def drawGrid(x,y,block):
    rect = pygame.Rect(x*blockS, y*blockS, blockS, blockS)
    pygame.draw.rect(screen, GRAY, rect, 1)

#Works!
def checkSurrounding(x,y,block):
    totalNearby = 0
            
    #Checks top-left, top-middle, & left
    if block[y-1][x-1]:
        totalNearby += 1
    if block[y-1][x]:
        totalNearby += 1
    if block[y][x-1]:
        totalNearby += 1
        
    ###            
    #Determines if x-coordinate is at edge of screen (block[y]-1)
    #If True, check at [0]
    if x == len(block[y])-1:
        if block[y-1][0]:
            totalNearby += 1
        if block[y][0]:
            totalNearby += 1
    #Otherwise, check at index [x]+1
    else:
        if block[y-1][x+1]:
            totalNearby += 1
        if block[y][x+1]:
            totalNearby += 1
    ###            
    
    ###
    #Determines if y-coordinate is at edge of screen (block-1)            
    #If True, check at [0] 
    if y == len(block)-1:
        if block[0][x-1]:
            totalNearby += 1
        if block[0][x]:
            totalNearby += 1
                    
        #BUT if x-coordinate is also at edge of screen (block[y]-1), check at index [0][0]  
        if x == len(block[y])-1:
            if block[0][0]:
                totalNearby += 1
                
        #Otherwise, check at index [0][x+1]
        else:
            if block[0][x+1]:
                totalNearby += 1
                        
    #If False, check normally at [y+1]
    else:
        if block[y+1][x-1]:
            totalNearby += 1
        if block[y+1][x]:
            totalNearby += 1
                    
        #BUT if x-coordinate is at edge of screen (again), check at index [y+1][0]  
        if x == len(block[y])-1:
            if block[y+1][0]:
                totalNearby += 1
                        
        #Otherwise check at index [y+1][x+1]
        else:       
            if block[y+1][x+1]:
                totalNearby += 1
    ###            
            
    #Check totalNearby & Apply Rules
    if totalNearby == 3:
        nextBlock[y][x] = True
    elif totalNearby == 2:
        nextBlock[y][x] = block[y][x]
    else:
        nextBlock[y][x] = False
                
    totalNearby = 0
    return

def updateBlock(x,y,block):
    #Update block from nextBlock
    block[y][x] = nextBlock[y][x]

#https://pythonprogramming.altervista.org/pygame-how-to-display-the-frame-rate-fps-on-the-screen/
def updateText(generation):
    fps = "Generation: " + str(generation) + " Generations/sec: " + str(int(clock.get_fps())//speed)
    fpsText = font.render(fps, 1, pygame.Color("Blue"))
    return fpsText
     
#########################CALL

#Call main loop            
main()
