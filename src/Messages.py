
# Standardized message strings for networked communication

# Only ever issued by a client upon initial connection
MSG_HELLO = "HELLO".encode("utf-8")

# Request to obtain key
MSG_GETKEY = "GETKEY".encode("utf-8")

# Connection attempt has been blocked
MSG_BLOCK = "BLOCK".encode("utf-8")

# Request has been denied
MSG_DENY = "DENY".encode("utf-8")

# Connection should close
MSG_EXIT = "EXIT".encode("utf-8")

#
MSG_NULLSTR = "".encode("utf-8")
