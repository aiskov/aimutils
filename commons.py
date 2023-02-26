import sys


def crop_slash(s: str) -> str:
    if s.startswith('/'):
        return s[1:]

    return s


if __name__ == '__main__':
    print('This script cannot be run as the main program. Import it into another script instead.')
    sys.exit(1)
