def input_int(text):
    while True:
        try:
            in_int = int(input(text))
            break
        except KeyboardInterrupt:
            break
        except:
            pass
    return in_int