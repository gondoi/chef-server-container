# -*- mode: ruby -*-
# vi: set ft=ruby :

$setup1 = <<SCRIPT1
# misc tools
apt-get -qq update
apt-get install -y vim byobu curl

# install the latest docker
curl -sSL https://get.docker.com/ubuntu/ | sudo sh
usermod -G docker -a vagrant
SCRIPT1

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provider "virtualbox" do |v|
    v.memory = 768
  end

  config.vm.box = "opscode-ubuntu-14.04"
  config.vm.box_url = "http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_ubuntu-14.04_chef-provisionerless.box"

  config.vm.network :forwarded_port, guest: 8443, host: 8443
  # config.vm.network :private_network, ip: "192.168.33.10"
  # config.vm.network :public_network

  # config.omnibus.chef_version = :latest
  # config.berkshelf.enabled = true

  # config.vm.provision :chef_solo do |chef|
  #   chef.add_recipe "docker"
  #
  #   chef.json = {}
  # end

  config.vm.provision "shell", inline: $setup1
end
