from processed import Processed


def main() -> None:
    pro: Processed = Processed()
    [print(x) for x in pro.get_files()]


if __name__ == "__main__":
    main()
