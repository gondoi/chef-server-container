FROM ubuntu:14.04

# Set locale to avoid apt-get warnings in OSX
RUN locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8
ENV LC_ALL C
ENV LC_ALL en_US.UTF-8

# Install curl and certifications to allow download of install.sh
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
      curl \
      ca-certificates \
      python-pip \
      git-core \
      && \
    apt-get clean && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*
RUN curl -L https://www.opscode.com/chef/install.sh | bash -s -- -P server

RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -sf /bin/true /sbin/initctl

COPY chef-server.rb /etc/chef-server/

RUN /opt/chef-server/embedded/bin/runsvdir-start & \
    chef-server-ctl reconfigure && \
    chef-server-ctl stop

# Add chefdk gem installs and embedded binaries to the PATH
ENV PATH $PATH:/opt/chef-server/embedded/bin

ADD requirements.txt /root/
RUN pip install -r /root/requirements.txt

ADD chef_proxy.py /root/

# Clean up
RUN rm -rf /tmp/* /var/tmp/* /opt/chef-server/embedded/lib/ruby/gems/2.1.0/cache/*

COPY start.sh /usr/local/bin/

ENTRYPOINT ["/usr/local/bin/start.sh"]
