glow_jenkins_glow
=================

A little script to visualize the [jenkins](http://jenkins-ci.org/) status on a raspberry pi with a [piglow](http://shop.pimoroni.com/products/piglow) modul.

## Install
1. `git clone https://github.com/xsteadfastx/glow_jenkins_glow.git /opt/glow_jenkins_glow`
2. `cd /opt/glow_jenkins_glow`
3. `virtualenv --system-site-packages env`
4. `source bin/active`
5. `python glow_jenkins_glow.py`
6. Enjoy the blinkenlights!11!!!!

## Using with supervisord
Here a config example:

```
[program:glow_jenkins_glow]
command=python /opt/glow_jenkins_glow/glow_jenkins_glow.py
directory=/opt/glow_jenkins_glow
environment=PATH="/opt/glow_jenkins_glow/env/bin"
user=root
autostart=yes
```
