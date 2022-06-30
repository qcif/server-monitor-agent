# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 2.2.0"
Vagrant.configure("2") do |config|

  guest_user_name = "vagrant"
  guest_home = "/home/#{guest_user_name}"
  guest_src_dir = "#{guest_home}/src"
  ansible_venv_dir = "#{guest_home}/ansible-venv"
  python_version = "3.9"

  # --- Host and Guest Paths ---

  # sync folder using rsync option
  rsync_exclude_list = %w[.vagrant/ .git/ .idea/ coverage-html/ __pycache__/ venv/]
  config.vm.synced_folder '.', guest_src_dir, type: "rsync", rsync__exclude: rsync_exclude_list

  # --- Common Options ---

  # the base box to use - most recent Ubuntu LTS
  config.vm.box = "generic/ubuntu2004"

  # the vm name
  vm_hostname = "server-monitor-agent"

  # set hostname
  config.vm.hostname = vm_hostname

  # --- Provider-specific Options ---
  # update these if necessary - try with the defaults first

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024  # in MB
    v.cpus = 1
    v.name = vm_hostname
    v.gui = false
  end

  # --- Run script then ansible to set up guest ---

  # Set this to a local ubuntu mirror to speed up the apt package installations.
  # Find your local mirrors here: https://launchpad.net/ubuntu/+archivemirrors
  old_apt_url = 'http://us.archive.ubuntu.com/ubuntu'
  new_apt_url = 'https://mirror.aarnet.edu.au/pub/ubuntu/archive'
  ubuntu_release = 'focal'
  config.vm.provision "install_ansible", type: "shell", inline: <<-SHELL
    # vagrant might require a /vagrant directory
    if [[ ! -d "/#{guest_user_name}" ]]; then
      sudo mkdir -p "/#{guest_user_name}"
      sudo chown "#{guest_user_name}:#{guest_user_name}" "/#{guest_user_name}"
    fi

    # always update apt packages
    sudo DEBIAN_FRONTEND=noninteractive apt-get -yq update

    # ensure ca-certificates is up to date so that https connections will work
    sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install ca-certificates

    # update apt source to a local mirror to speed up the first apt update
    if [[ -f /etc/apt/sources.list && $(grep "#{old_apt_url}" /etc/apt/sources.list) ]]; then
      sudo sed -i 's;#{old_apt_url};#{new_apt_url};g' '/etc/apt/sources.list'
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq update
    fi
    if [[ -f /etc/apt/sources.list.save && $(grep "#{old_apt_url}" /etc/apt/sources.list.save) ]]; then
      sudo sed -i 's;#{old_apt_url};#{new_apt_url};g' '/etc/apt/sources.list.save'
    fi

    sudo DEBIAN_FRONTEND=noninteractive apt-get -yq update

    # provide Python
    if [ ! -f "/etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-#{ubuntu_release}.list" ]; then
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq upgrade
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install software-properties-common python3-apt python-apt-common python3-packaging apt-transport-https
      sudo DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:deadsnakes/ppa
    fi

    # create a Python virtual env for ansible
    if [ ! -d "#{ansible_venv_dir}" ]; then
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq update
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq upgrade
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install python#{python_version} python#{python_version}-dev python#{python_version}-venv python#{python_version}-distutils
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install libxml2-dev libxslt-dev zlib1g-dev libffi-dev
      sudo python#{python_version} -m venv "#{ansible_venv_dir}"
      sudo chown -R "#{guest_user_name}:#{guest_user_name}" "#{ansible_venv_dir}"
    fi

    sudo DEBIAN_FRONTEND=noninteractive apt-get -yq upgrade
    sudo DEBIAN_FRONTEND=noninteractive apt-get -yq autoremove
    sudo DEBIAN_FRONTEND=noninteractive apt-get -yq autoclean

    "#{ansible_venv_dir}/bin/python" -m pip install -U pip
    "#{ansible_venv_dir}/bin/pip" install -U setuptools wheel
    "#{ansible_venv_dir}/bin/pip" install -U lxml
    "#{ansible_venv_dir}/bin/pip" install -U ansible 'ansible-lint'

    "#{ansible_venv_dir}/bin/ansible-galaxy" collection install -p /home/vagrant/ansible-collections --upgrade community.general
  SHELL

  config.vm.provision "run_ansible", type: "ansible_local" do |ans|
    ans.compatibility_mode = "2.0"
    ans.verbose = false
    ans.install = false
    ans.playbook_command = "#{ansible_venv_dir}/bin/ansible-playbook"
    ans.config_file = "#{guest_src_dir}/ansible/ansible.cfg"
    ans.playbook = "#{guest_src_dir}/ansible/playbook.yml"
    ans.extra_vars = {
        'guest_src_dir': guest_src_dir,
        'guest_user_name': guest_user_name,
        'python_version': python_version,
    }
  end

end
