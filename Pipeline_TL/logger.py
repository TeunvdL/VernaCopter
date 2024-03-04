class logger:
    def color_text(text, color):
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'orange': '\033[38;5;208m',
            'reset': '\033[0m'
        }
        return colors[color] + text + colors['reset']