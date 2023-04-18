import numpy as np
import os

class Helper():
    
    @staticmethod
    def get_file_names(rel = '.') -> list[str]:
        print(os.getcwd())
        return [
            rel + '/txt/signal_omega0=19.1_a0_1=0.01.txt',
            rel + '/txt/signal_omega0=19.1_a0_1=0.02.txt',
            rel + '/txt/signal_omega0=19.1_a0_1=0.03.txt',
            rel + '/txt/signal_omega0=19.1_a0_1=0.04.txt',
            rel + '/txt/signal_omega0=19.1_a0_1=0.05.txt',

            rel + '/txt/signal_omega0=19.2_a0_1=0.01.txt',
            rel + '/txt/signal_omega0=19.2_a0_1=0.02.txt',
            rel + '/txt/signal_omega0=19.2_a0_1=0.03.txt',
            rel + '/txt/signal_omega0=19.2_a0_1=0.04.txt',
            rel + '/txt/signal_omega0=19.2_a0_1=0.05.txt',

            rel + '/txt/signal_omega0=19.3_a0_1=0.01.txt',
            rel + '/txt/signal_omega0=19.3_a0_1=0.02.txt',
            rel + '/txt/signal_omega0=19.3_a0_1=0.03.txt',
            rel + '/txt/signal_omega0=19.3_a0_1=0.04.txt',
            rel + '/txt/signal_omega0=19.3_a0_1=0.05.txt',

            rel + '/txt/signal_omega0=19.4_a0_1=0.01.txt',
            rel + '/txt/signal_omega0=19.4_a0_1=0.02.txt',
            rel + '/txt/signal_omega0=19.4_a0_1=0.03.txt',
            rel + '/txt/signal_omega0=19.4_a0_1=0.04.txt',
            rel + '/txt/signal_omega0=19.4_a0_1=0.05.txt',

            rel + '/txt/signal_omega0=19.5_a0_1=0.01.txt',
            rel + '/txt/signal_omega0=19.5_a0_1=0.02.txt',
            rel + '/txt/signal_omega0=19.5_a0_1=0.03.txt',
            rel + '/txt/signal_omega0=19.5_a0_1=0.04.txt',
            rel + '/txt/signal_omega0=19.5_a0_1=0.05.txt',
        ]
    
    @staticmethod
    def get_omega0(file_name) -> float:
        return float(file_name.split('_a0_1=')[0].split('signal_omega0=')[1])
    
    @staticmethod
    def get_a0_1(file_name) -> float:
        return float(file_name.split('.txt')[0].split('a0_1=')[1])