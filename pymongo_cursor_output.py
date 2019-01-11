import pager
import pprint
import os
import platform


def page_print(cursor):
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

    for i in cursor:
        text = pprint.pformat(i)
        lines = text.split('\n')
        count = 1
        for l in lines:
            print(l)
            count += 1
            if pager.getheight()-3 == count:
                print('hit return to continue')
                in_str = input()
                if len(in_str) > 0:
                    return
