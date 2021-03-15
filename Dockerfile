# image based on debian
FROM debian:latest

# update package lists
RUN apt-get update -y


# workaround for avoiding debconf failure messages
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# install all packages required to compile and run tor within the container 
RUN apt-get install libssl-dev -y -qq > /dev/null
RUN apt-get install zlib1g-dev -y -qq > /dev/null
RUN apt-get install python3 -y -qq > /dev/null
RUN apt-get install python3-pip -y -qq > /dev/null
RUN apt-get install libevent-dev -y -qq > /dev/null

# create directories
RUN mkdir -p /home/script
RUN mkdir -p /home/tor
RUN mkdir -p /etc/tor
RUN mkdir -p /var/log/tor
RUN mkdir -p /var/lib/tor
RUN mkdir -p /run/tor

# init file, tor binaries and torrc file

# the init handles execution parameters (which analysis should be started, V2, V3, V3VN, V3NE?)
ADD init_tor.sh /home/script/init_tor.sh

# tor source code, which is compiled within the container (should be kept up-to-date)
ADD tor /home/tor

# tor config file 
ADD torrc /etc/tor/torrc

# vanguards config file
ADD vanguards.conf /etc/tor/vanguards.conf

# python requirements (currently only stem)
ADD requirements.txt /home/requirements.txt

# iinstall python package manager
RUN pip3 install --upgrade pip

# install required packages (currently only stem)
RUN pip3 install -r /home/requirements.txt

# install vanguards (could also be done within the requirements file)
RUN pip3 install vanguards

# create log files
RUN touch /var/log/tor/debug.log
RUN touch /var/log/tor/info.log
RUN touch /var/log/tor/notices.log 

# build custom tor binary
RUN sh ./home/tor/configure
RUN chmod +x /home/tor/install-sh
RUN make && make install

RUN chmod +x /home/script/init_tor.sh
RUN chmod 700 /var/lib/tor

# add timing analysis folder
ADD timing-analysis/ /home/timing-analysis/

# run init script
ENTRYPOINT ["/bin/bash","/home/script/init_tor.sh"]
