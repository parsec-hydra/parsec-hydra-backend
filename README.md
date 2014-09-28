Parser Hydra
============
Cool stuff using the Nod ring.

[Presentation](https://docs.google.com/presentation/d/11Wawv21vLjM40EVG0sK-bvuBOjdmjVHvc-LBMAJQ1FU/edit?usp=sharing)

Nod ring Bluetooth specification
--------------------------------
The full Bluetooth specification is 
[available on GitHub](https://github.com/openspatial/openspatial-android-sdk/raw/master/sdk/OpenSpatial.pdf).

Enable notifications on 6D
--------------------------

    char-write-req 0x004c 0100 # enable
    char-write-req 0x004c 0000 # disable

Notify endpoint
---------------

    http://<host>/<device>/00000002-0000-1000-8000-a0e5e9000000/00000205-0000-1000-8000-a0e5e9000000/notify

http://localhost:5000/A0:E5:E9:00:01:F2/00000002-0000-1000-8000-a0e5e9000000/00000205-0000-1000-8000-a0e5e9000000/notify
