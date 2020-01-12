if __name__ == '__main__':
    import dropbox
    from sys import argv, exit

    if len(argv) < 2:
        exit(1)
    access_token = argv[1]
    try:
        client = dropbox.Dropbox(argv[1])
        client.users_get_current_account()
    except Exception:
        exit(1)
