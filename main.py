"""Here you can define your custom filter rules"""

from filter import USOSFilter

if __name__ == '__main__':
    pass
    """ Example usage
    test = USOSFilter('https://rejestracja.usos.uw.edu.pl/catalogue.php?rg=0000-2021-OG-UN')
    test.add_condition(lambda x: float(x['ects']) >= 4)
    test.show()
    """
