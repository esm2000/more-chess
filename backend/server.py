import logging


logging.basicConfig(
    format="%(asctime)s %(message)s", datefmt="%m/%d/%Y | %I:%M:%S%p | " + ":"
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main():
    while True:
        pass


if __name__ == "__main__":
    logging.info('running')
    main()