import numpy as np
import json
import os

class Helper():
    __colors__ = None

    @classmethod
    def colors(cls, color_theme_path = 'color_theme.json'):
        if cls.__colors__ == None:
            with open(color_theme_path) as f:
                color_theme_config = json.load(f)

            active_theme = color_theme_config['active_theme']
            color_themes = color_theme_config['color_themes']
            hsa_color_themes = color_themes['hsa_map']
            lesssa_color_themes = color_themes['lesssa_map']
            color_theme = {
                'hsa_map': hsa_color_themes[active_theme],
                'lesssa_map': lesssa_color_themes[active_theme]
            }
            cls.__colors__ = color_theme
        
        return cls.__colors__

    @staticmethod
    def get_file_names(rel = '.') -> list[str]:
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