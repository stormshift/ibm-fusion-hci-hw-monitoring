# IBM Fusion HCI Hardware Monitoring via ServiceNode

Run `check_ipmi.py` example:

```shell
./check_ipmi.py -H <HOST>
    -U <USER>
    -P <PASSWORD>
    -E <sensor  entity id>
    -W <warnind threashold>
    -C <criticial threadshold>
```

Example:
```
check_ipmi.py -H 169.253.1.3 -U CEUSER  -P xxxx -E 39.1 -W 25 -C 30
OK - Ambient Temp 18 degrees C | Ambient_Temp=18.0;25.0;30.0
```

IPMI Tool execution
```
% ipmitool  -H 169.253.1.3 -U  USER -P XXXX -I lanplus sdr entity 39.1 -c
Ambient Temp,18,degrees C,ok
```
