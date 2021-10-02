##CONTROLS##
# LEFT CLICK to add start, end and obstances ##
## RIGHT CLICK to remove boxes ##
## SPACE to start pathfinding ##
## C TO CLEAR ##
## G TO GENERATE MAZE ##
import pygame
from queue import PriorityQueue
import random

WIDTH = 848
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

#Colour constants
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
GREY = (128,128,128)
TURQUOISE = (64,224,208)
MAGENTA = (255,0,255)
LBLUE = (51,204,255)


class Node(object):
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.colour = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows
        
    def get_pos(self):
        #Return y then x 
        return self.row,self.col

    def is_closed(self):
        return self.colour == RED
    
    def is_open(self):
        return self.colour == GREEN
    
    def is_barrier(self):
        return self.colour == BLACK
    
    def is_start(self):
        return self.colour == ORANGE
    
    def is_end(self):
        return self.colour == BLUE
    
    def reset(self):
        self.colour = WHITE
        
    def make_start(self):
        self.colour = ORANGE
    
    def make_closed(self):
        self.colour = RED
        
    def make_open(self):
        self.colour = GREEN
        
    def make_barrier(self):
        self.colour = BLACK
    
    def make_end(self):
        self.colour = BLUE
        
    def make_path(self):
        self.colour = LBLUE

    def make_traversed(self):
        self.colour = MAGENTA
        
    def draw(self,win):
        pygame.draw.rect(win,self.colour,(self.x,self.y,self.width,self.width))
        
    def update_neighbours(self,grid):
        self.neighbours = []
        
        #Check UNDER
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_barrier():
            self.neighbours.append(grid[self.row + 1][self.col])
         
        #Check ABOVE
        if self.row > 0 and not grid[self.row-1][self.col].is_barrier():
            self.neighbours.append(grid[self.row - 1][self.col])
            
        #Check RIGHT
        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_barrier():
            self.neighbours.append(grid[self.row][self.col+1])
            
        #Check LEFT
        if self.col > 0 and not grid[self.row][self.col-1].is_barrier():
            self.neighbours.append(grid[self.row][self.col-1])
        
    
    def __lt__(self,other):
        return False


#Heuristic function passing in 2 points with x y cooridinates
def h(p1,p2):
      x1,y1 = p1
      x2,y2 = p2
      #Return manhattan distance
      return abs(x1-x2) + abs(y1-y2)


#Creating path from end to start node along shortest path
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        #Sets current to node visited before
        current = came_from[current]
        #Colouring the path
        current.make_path()
        draw()

  
#A* algorithm  
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    
    #Add fscore, number and start node 
    open_set.put((0, count, start))
    came_from = {}
    
    #Set all distances from the start node to infinity
    g_score = {node:float("inf") for row in grid for node in row}
    g_score[start] = 0
    
    #Set all predicted distances to the end node to infinity
    f_score = {node:float("inf") for row in grid for node in row}
    #Heuristic
    f_score[start] = h(start.get_pos(), end.get_pos())
    
    #Keeps track of items in the priority queue
    open_set_hash = {start}
    
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        #Get node which has the lowest cost function      
        current = open_set.get()[2]
        #Removes node to synchronize with queue
        open_set_hash.remove(current)
        
        #Found end node
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
        
        for neighbour in current.neighbours:
            temp_g_score = g_score[current]+1
            
            #If there is a shorter path to a node, then update the distance
            if temp_g_score < g_score[neighbour]:                
                #Update with shorter path
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
                
                #Add neighbour node into hash and queue
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour],count,neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()
        draw()
        
        if current !=start:
            current.make_closed()
 
    return False


#Making a grid       
def make_grid(rows, width):
    grid = []
    #Give width and height of cubes 
    gap = width // rows
    #Fill grid
    for i in range(rows):
        #Add new row
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            #Add node object to row
            grid[i].append(node)
    return grid


#Draw gridlines
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        #Horizontal line every *gap* pixels
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            #Vertical line every *gap* pixels
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


#Drawing background, nodes and gridlines   
def draw(win, grid, rows, width):
    win.fill(WHITE)
    
    for row in grid:
        for node in row:
            node.draw(win)
            
    draw_grid(win, rows, width)
    
    pygame.display.update()
    

#Finding position of mouse click
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x,y = pos
    
    row = y // gap
    col = x // gap
    
    return row, col


def create_maze_grid(grid, ROWS):
#fill columns
    for i in range(1,ROWS-1):
        if i % 2 == 1:
            for j in range(1,ROWS-1):
                grid[i][j].make_barrier()
                grid[j][i].make_barrier()    

    return grid


def generateMaze(grid, ROWS, win):    
    

    grid = create_maze_grid(grid, ROWS) #generate maze gridlines
    
    stack = []
    visited = [[0 for x in range(ROWS)] for y in range(ROWS)] #visited matrix    
    
    r,c = (2,2) #x y coordinates of starting cell
    stack.append((r,c))  
    visited[r][c] = 1

    maxn = 51 #maximum column and row index
    minn = 2  #minimum column and row index
    
    while len(stack) > 0:
        
        cells = []

        #right cell
        if c + 2 < maxn:
            if not visited[r][c+2]:
                cells.append((r,c+2,'r'))

        #left cell
        if c - 2 >= minn:
            if not visited[r][c-2]:
                cells.append((r,c-2,'l'))

        #cell above
        if r - 2 >= minn:
            if not visited[r-2][c]:
                cells.append((r-2,c,'u'))

        #cell below
        if r + 2 < maxn:
            if not visited[r+2][c]:
                cells.append((r+2,c,'d'))     
        

        if len(cells) > 0:
            newr, newc, dir = random.choice(cells)
            stack.append((newr,newc))
            visited[newr][newc] = 1            

            #remove barrier depending on direction
            if dir == 'r':
                grid[r][c+1].reset() 
            elif dir == 'l':
                grid[r][c-1].reset()
            elif dir == 'u':
                grid[r-1][c].reset()
            else:
                grid[r+1][c].reset()
        else:
            r,c = stack.pop()
            grid[r][c].make_traversed() #draw backtracking cell            
            draw(win, grid, ROWS, WIDTH)
            grid[r][c].reset()

    return grid


#MAIN
def main(win, width):
    ROWS = 53
    grid = make_grid(ROWS, width)
    
    start = None
    end = None
    
    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            #left mouse click
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                
                #If we havent made a starting node, then make one with mouse click
                #!=end stops the starting node from being at the same position of the ending node
                if not start and node!=end:
                    start = node
                    start.make_start()
                #If we havent made an end node, then make one with mouse click
                elif not end and node!=start:
                    end = node
                    end.make_end()
                
                elif node != end and node !=start:
                    node.make_barrier()
                
                    
            #Right mouse click will earse the spot
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None
        
            if event.type == pygame.KEYDOWN:
                #Start algorithm if space is pressed
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                #Resetting
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
                #Generating maze
                if event.key == pygame.K_g:
                    start = None
                    end = None
                    grid = generateMaze(grid, ROWS, win)
                    

                
    pygame.quit()


main(WIN, WIDTH)
