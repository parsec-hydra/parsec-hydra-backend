Mimic game
==========

Mechanics
---------
* repeat data by moving
* using the Nod Ring gyroscope and accelerometer

Implementation
--------------
* connect the device (through admin ui)
* threading in Python to parallellize data treatment (ThreadPool and map)
* parsing/filtering data
* process data required by the front-end

Server framework
----------------
* Flask
* https://pypi.python.org/pypi/Flask-uWSGI-WebSocket/0.2.5

Threading
---------
* https://pypi.python.org/pypi/threadpool/1.2.7
* https://pypi.python.org/pypi/futures

Bluetooth
---------
* https://pypi.python.org/pypi/BT-Manager/0.3.0
* https://pypi.python.org/pypi/PyBluez/0.20

Heavy computation
-----------------
The device will provide us a list of 3-tuple of acceleration and a 2-tuple 
orientation both based on time.

We have to rotate the acceleration tuple using a rotational matrix. Angles will
be calculated by using the 2-tuple orientation in a way we always rotate the
acceleration data in the same reference axis. This operation takes 9
multiplications and 3 sums for each element in the list.

Every calculated trajectories must use the same time system, so that polynoms 
are easily comparable. We therefore any calculation on a zero-starting time 
system.

    `t_n' = t_n - t_0` for each tn in the list

Then we calculate a polynom of the 3-tuple list of accelerations for each 
dimensions. A polynom is represented as a n-tuple from power of 0 to power of 
`n - 1`.
    
   `p_x = polynomize(x, t)`

To compare 2 polynoms `p_1` and `p_2`, we calculate

    `integral(abs(p_1 - p_2))`

We evaluate the integral from the beginning of the movement to its end. If two
movements are aligned in term of accelerations, they are considered equal. What
matters is the difference between these two.

Two trajectories are compared this way

function of time.

We can calculate a rotation matrix between each orientation tuple and a norm.

Given a list of 3-tuple acceleration and orientation, calculate a polynom for
each dimensions in terms of unit of time t.
* numpy
* http://docs.scipy.org/doc/numpy/reference/generated/numpy.polyfit.html

Communication
-------------
* https://pypi.python.org/pypi/Flask-uWSGI-WebSocket/0.2.5
