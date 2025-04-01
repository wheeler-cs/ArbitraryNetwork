
# Standardized message strings for networked communication

# Connection-related messages
MSG_HELLO = "HELLO".encode("utf-8") # Only ever issued by a client upon initial connection
MSG_BLOCK = "BLOCK".encode("utf-8") # Connection attempt has been blocked
MSG_EXIT  = "EXIT".encode("utf-8")  # Connection should close

# Operation messages
MSG_GETKEY = "GETKEY".encode("utf-8") # Request to obtain key
MSG_ISKEY  = "ISKEY".encode("utf-8")  # Rest of message contains key
MSG_DENY   = "DENY".encode("utf-8")   # Request has been denied

# Utility messages
MSG_NULLSTR = "".encode("utf-8") # Returned by crashed clients
