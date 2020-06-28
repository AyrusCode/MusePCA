"""Generate sound-only auditory oddball stimulus presentation.
"""
import time
from optparse import OptionParser

import numpy as np
import pygame
from pandas import DataFrame
from psychopy import visual, core, event, sound
from pylsl import StreamInfo, StreamOutlet



def present(duration=120):
    BLUE = (0,0,255)
    BLACK = (0,0,0)
    RED = (255,0,0)
    YELLOW = (255,255,0)
    WHITE = (255,255,255)
    
    X = 1080
    Y = 720
    
    info = StreamInfo('Markers', 'Markers', 1, 0, 'float32', 'myuidw43536')
 
    outlet = StreamOutlet(info)    

    #np.random.seed(random_state)
    #1 is up, 2 is nothing
    markernames = [1, 2]
    randnums= np.random.randint(1,3,200)
    iterator = 0
    start = time.time()
    secs = 0.07
    
    # Set up trial parameters
    record_duration = np.float32(duration)

    # Initialize audio stimuli
    aud1 = sound.Sound(440,secs=secs)#, octave=5, sampleRate=44100, secs=secs)
    aud1.setVolume(0.8)
    
    pygame.init()
    # Setup graphics
    screen = pygame.display.set_mode((X, Y), pygame.RESIZABLE)
    
   
    while True:
            event = pygame.event.wait()
            if event.type == pygame.MOUSEBUTTONDOWN:
                break
                
    while iterator < 200 : #or (time.time() - start > record_duration)
        pygame.init()
        
        word = ""
        wordd = ''
        
        if randnums[iterator] == 1:
            word = "up"
            wordd = 'up'
        
        elif randnums[iterator] == 2:
            word = "nothing"
            wordd = 'nothing'
            
        iterator = iterator + 1
        
        # set the pygame window name 
        pygame.display.set_caption(word + " - Displaying for  second") 
        
        font = pygame.font.Font(pygame.font.get_default_font(), 36)
        text_surface = font.render(wordd, 1, pygame.Color('white'))
        screen.blit(text_surface, dest=(540,360))
        pygame.display.flip()
     
        pygame.display.update()
        
        pygame.event.get()
        pygame.time.wait(1000)

        pygame.draw.rect(screen, BLACK, (0,0, X, Y))
        pygame.draw.circle(screen, BLUE, (540, 360), 5)
        pygame.display.update()
        
        # wait 4s
        pygame.display.set_caption("Wait 4 seconds for the beep and think about the direction presented") 
        pygame.event.get()
        pygame.time.wait(4000)
        
        
        # present dot/crosshair to focus on for 5 seconds and play sound
        pygame.display.set_caption("Displaying, please attend to the direction")
        pygame.draw.circle(screen, RED, (540, 360), 5)
        pygame.display.update()
        aud1.stop()        
        aud1.play()
        timestamp = time.time()
        outlet.push_sample([randnums[iterator]], timestamp)
        pygame.event.get()
        pygame.time.wait(1000)
    


        pygame.display.set_caption("Done, take 3 seconds to rest")
        pygame.draw.rect(screen, BLACK, (0,0, X, Y))
        pygame.display.update()
        pygame.event.get()
        pygame.time.wait(3000)

 
        
    # Cleanup
    pygame.quit()
    exit()
        
        
    return trials


def main():
    parser = OptionParser()

    parser.add_option(
        '-d', '--duration', dest='duration', type='int', default=10,
        help='duration of the recording in seconds.')
    parser.add_option(
        '-n', '--n_trials', dest='n_trials', type='int', 
        default=10, help='number of trials.')
    parser.add_option(
        '-i', '--iti', dest='iti', type='float', default=0.3,
        help='intertrial interval')
    parser.add_option(
        '-s', '--soa', dest='soa', type='float', default=0.2,
        help='interval between end of stimulus and next trial.')
    parser.add_option(
        '-j', '--jitter', dest='jitter', type='float', default=0.2,
        help='jitter in the intertrial intervals.')
    parser.add_option(
        '-e', '--secs', dest='secs', type='float', default=0.2,
        help='duration of the sound in seconds.')
    parser.add_option(
        '-v', '--volume', dest='volume', type='float', default=0.8,
        help='volume of the sounds in [0, 1].')
    parser.add_option(
        '-r', '--randomstate', dest='random_state', type='int', 
        default=42, help='random seed')

    (options, args) = parser.parse_args()
    trials_df = present(
        duration=options.duration, n_trials=options.duration, 
        iti=options.iti, soa=options.soa, jitter=options.jitter,
        secs=options.secs, volume=options.volume, 
        random_state=options.random_state) 

    print(trials_df)


if __name__ == '__main__':
    main()
