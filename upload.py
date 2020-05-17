import os
from _socket import MSG_WAITALL

DEFAULT_BUFF = 2048


def send(file_name, connection):  # send files to client
    connection.sendall('send\n'.encode('UTF-8'))  # alert client
    print('sent')
    i = file_name.rfind('/')  # find index of last / in file destination
    connection.sendall(file_name[i + 1:].encode('UTF-8'))  # send filename without the destination
    connection.recv(1)  # wait for ack

    totalbytes = os.path.getsize(file_name)
    connection.sendall(str(totalbytes).encode('UTF-8'))
    response = connection.recv(1).decode('UTF-8')  # wait for ack

    if response == 'K':
        file = open(file_name, 'rb')  # opens file and reads it in byte form
        buffer = file.read(2048)  # read 2048 bytes from file to buffer
        while buffer:
            connection.sendall(buffer)
            buffer = file.read(2048)  # read next 2048 bytes
        file.close()
    response = connection.recv(1).decode('UTF-8')
    if response == 'K':
        print('File uploaded successfully')


def download(file_path, connection):  # upload files from client to server
    #  figures out file name in windows path
    file_name = (file_path[file_path.rfind('\\') + 1:])

    connection.sendall('download\n'.encode('UTF-8'))

    connection.sendall(file_path.encode('UTF-8'))  # alert client to wanted file
    response = connection.recv(1).decode('UTF-8')  # wait for client ack

    # correct ack if file found
    if response == 'K':
        str_size = connection.recv(10).decode('UTF-8')  # file size sent by client
        # remove any extra /0 from C send value and turns to int
        size = int(str_size[:str_size.find('\x00')])

        print('file size: ', size)

        connection.sendall('K'.encode('UTF-8'))
        file = open(file_name, 'wb')  # open file in write binary mode

        amt_recv = 0
        over = size % DEFAULT_BUFF  # finds size of last buffer
        while amt_recv < size:
            if size - amt_recv < DEFAULT_BUFF:
                tmpbuff = connection.recv(over, MSG_WAITALL)  # recv remaining bytes
                file.write(tmpbuff)
                break
            buffer = connection.recv(DEFAULT_BUFF, MSG_WAITALL)
            amt_recv += DEFAULT_BUFF  # increment by 2048/buffer size
            file.write(buffer)
        file.close()
        print("fill successfully downloaded")
