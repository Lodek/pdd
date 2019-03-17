



class SigGen:
    updater = None
    def okay(self):
        for signal in self.signals:
            self.updater.upate()
            yield signal


class Clock(SigGen):
    self.signal = 0
    def signals(self):
        t = self.signal
        self.signal = 1 if self.signal == 0 else 0
        yield t

clock = Clock()
clock.bus = bus

for signal in clock.okay():
    #do stuff to circuits, thing calls update at the end of the cycle
    
