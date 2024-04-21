# Ubuntu on Asus ROG Zephyrus G14 2021 (Setup guide)

Here is a way to do a robust install of Ubuntu (+ optional Windows 11 dual boot and LUKS encryption) on an Asus laptop, with minimal usable hardware support, without a significant amount of tinkering that may break in future or require frequent technical attention.

**In summary, the key thing is to have an up to date kernel, which usually means disabling secure-boot and installing the latest stable (6.0+) using mainline or xanmod, and as well as making sure the latest nvidia driver and dkms is installed.**

## Specs:
* Model Asus G14 2021 (GA401QC)
* AMD R7 5800 8 core 16 thread (onboard Radeon graphics)
* NVIDIA RTX 3050 4GB (60W +15W boost)
* 40GB RAM (8GB soldered + 32GB stick added)
* 2TB SSD
* 14inch 1920x1080 Display @144Hz
* ~Mediatek Wifi 6 card~ Intel AX210 Wifi 6 card (Replaced built-in Mediatek card) 

## OS Install:
* Recommend disable secure boot (in BIOS) if you dont care about secure boot and would rather have freedom to install any unsigned kernel in future (recommended if you want unsigned Kernel 6.0+ with all the features working).
* Optionally dual boot: first install Windows 11 or 10 (you may need a USB ethernet/wifi dongle during install as Windows 11 may not have the wifi driver) from the prepared USB stick (turn off bitlocker for now), and resize its partition to say 1/4 the disk or so
1. Get Ubuntu 22.04 ISO burned onto a USB stick (e.g. using Balena Etcher). Could also use Kubuntu or other flavours.
2. Boot into the USB stick (repeatedly tap ESC during power on)
3. Its best to make sure you have an internet connection during install. If the built in wifi is not detected, get a USB wifi/ethernet dongle.
4. Start Ubuntu installer, I prefer minimal bloat install, and install all 3rd party/proprietary software.
5. If you want full disk encryption (LUKS), choose "something else" for partitions, and make a 1GB EXT4 partition mounted as `/boot` and the rest of the drive a container for encryption, then mount the contained EXT4 as `/`. DONT forget your encryption password!
6. Finish installation of Ubuntu and reboot.

## Software Setup:
1. Install [asusctl](https://gitlab.com/asus-linux/asusctl/) v4.0+. The Ubuntu repository has been deleted, so you can just manually build and install it (including rust/cargo) from source using these commands (if it doesnt work for you, try more [detailed instruction](https://gist.github.com/vijay-prema/cfcf8cc4085663b7bb48f34172c10629?permalink_comment_id=4431110#gistcomment-4431110).):
```
    git clone https://gitlab.com/asus-linux/asusctl.git
    cd asusctl
    apt install libclang-dev libudev-dev
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    make
    sudo make install
```
2. ~~OPTIONALLY Install GUI application [asusctl-gex](https://gitlab.com/asus-linux/asusctl-gex) gnome extension.~~ _Update Dec 2022: it seems this app is no longer updated and not recommended. Instead the latest asusctl already comes with a GUI called ROG Control Center, find it in your apps menu after intall, or run `rog-control-center` in terminal_
3. Install an up to date pipewire version and bluetooth audio support
```
sudo add-apt-repository ppa:pipewire-debian/pipewire-upstream
sudo apt install pipewire
sudo apt install libspa-0.2-bluetooth
```
4. Make sure recommended Ubuntu NVIDIA driver is installed (use "Additional Drivers" tool). Install nvidia-dkms as well which will enable the driver for 3rd party kernels (such as what I recommend in step 5 next) you might install in future `sudo apt install nvidia-dkms-525` (replace `525` with whatever NVIDIA driver version you have installed). Note: there is a partially open source "Open Kernel" version of the NVIDIA driver, I currently don't recommend this as it seems to have issues.
5. Optional but HIGHLY recommended, disable secure-boot in your BIOS, then install Kernel 6.1 or higher for Suspend and latest hardware support. An easy way is to install [Xanmod Kernel](https://xanmod.org/) 6.1 LTS, or alternatively use the [Mainline tool](https://ubuntuhandbook.org/index.php/2020/08/mainline-install-latest-kernel-ubuntu-linux-mint/).  Note that sometimes installing a very new kernel will result in NVIDIA driver not working, in this case, downgrade to previous.  If you use a LTS kernel you likely wont have this issue.
6. Reboot
7. ~~Enable the asusctl-gex extension in "Gnome Extensions" tool~~

## Quirks:
* **Errors while updating PPAs**: you may need to switch some repos distro branch from jammy to impish (or even hirsute if there is no impish) because jammy (Ubuntu 22.04) is too new. Do this in the "Software & Updates" app under the Other Software tab.  At some point most of these PPAs will catch up and you can change it back to impish.
* **Wayland**: The default login session for Ubuntu 22.04 is Wayland (rather than Xorg). It provides a smoother and more secure experience but has compatibility issues with some software (e.g. blank screen sharing in Discord):
   * To run an application with NVIDIA GPU in Wayland, you should right click on its icon and choose "Launch using Dedicated Graphics Card", for example Steam games (For Xorg graphics switching, just use the "Nvidia X Server" tool). Use `nvtop` (suggest installing [latest ppa version](https://launchpad.net/~flexiondotorg/+archive/ubuntu/nvtop)) to check what apps are using NVIDIA, or `radeontop` to check if AMD graphics is being used (although the latest nvtop version shows both nvidia and integrated radeon stats).
   * Worst case you can still log in as Xorg by clicking on the gear button bottom right before you press enter to login.  Personally I am sticking to xorg for now.
* **Keyboard LEDs flashing** during sleep mode: to stop them type `asusctl led-mode -s false`
* **Built in microphone** can be very noisy unless you turn its volume down to about 15%. If it still doesnt work at all or always shows as "unplugged" then try [this strange hack](https://askubuntu.com/questions/1218136/internal-microphone-doesnt-work-when-using-headphones/1357907#1357907).
* **Mute Microphone** key. There is a simple [hack](https://www.suyogjadhav.com/misc/2021/06/15/How-to-get-the-Asus-mic-key-working-in-Linux-on-Zephyrus-G14-(2021)/) to get this to work.
* **Battery maintenance**: You can keep the battery in better condition when you use the laptop mostly plugged in, by only charging to 60%: `asusctl -c 60`.
* **Disable boot up sound effect** - this can be disabled in the bios (tap ESC during power on) or run: `asusctl bios -p false`
* **Improve power efficiency** of NVIDIA card: `sudo sh -c 'echo \'options nvidia "NVreg_DynamicPowerManagement=0x02"\' > /etc/modprobe.d/nvidia.conf'` Then reboot.
* **Firefox high CPU usage** especially when playing youtube videos (e.g. 4k 60p video): Enable [video acceleration](https://ubuntuhandbook.org/index.php/2021/08/enable-hardware-video-acceleration-va-api-for-firefox-in-ubuntu-20-04-18-04-higher/).
  * `sudo apt install mesa-va-drivers`
  * Open Firefox and go to `about:config` in url bar. Then search for following keys, enable or disable them one by one:
    * `media.ffmpeg.vaapi.enabled` set to true
    * `media.ffvpx.enabled` set to false.
    * `media.rdd-vpx.enabled` set to false.
    * `media.rdd-process.enabled` set to false.
    * `media.navigator.mediadatadecoder_vpx_enabled` set to true.
    * If you experience page crashes, try setting `security.sandbox.content.level` to 0.
* **Google Chrome high CPU usage** especially when playing youtube videos (e.g. 4k 60p video): Enable [video acceleration](https://www.linuxuprising.com/2021/01/how-to-enable-hardware-accelerated.html) (*update: link possibly out of date for latest Chrome*).  Suggest also enabling these flags in the `chrome://flags` page:
    * `#ignore-gpu-blocklist`
    * `#enable-gpu-rasterization`
    * `#enable-zero-copy`
    * `#canvas-oop-rasterization`
    * Also try running with `google-chrome --enable-unsafe-webgpu --enable-features=Vulkan,UseSkiaRenderer`.  You can check gpu status by going to `chrome://gpu/` in the browser.
* **Suspend/sleep** In kernels older than 5.15 this has unpredictable behaviour (sometimes it might just work, other times it appears to work but fails to resume). To fix that, I HIGHLY recommend upgrading to kernel 6.1 or higher.  An easy way is to install [Xanmod Kernel](https://xanmod.org/) 6.1 LTS (also remember to install nvidia-dkms-* as mentioned earlier, to enable NVIDIA GPU for non-Ubuntu kernels).
* **Hibernate** To enable Hibernate (i.e. Suspend to Disk), first make sure swap file at [least as large as RAM](https://bogdancornianu.com/change-swap-size-in-ubuntu/) (e.g. I used 50GB for my 40GB RAM `bs=1G count=50`) and then [enable hibernate](https://www.linuxuprising.com/2021/08/how-to-enable-hibernation-on-ubuntu.html).

## Non-functioning and Semi-issues:
* **Fingerprint reader**. There are people [working on this](https://infinytum.co/fixing-my-fingerprint-reader-on-linux-by-writing-a-driver-for-it/) and making progress but it is very rudamentary. The real issue is even if they get it woring perfectly, this device cant work with multiple OS on the same system with dual boot, as each OS will try to install its own keys on the device causing conflict.
* **Mediatek Wifi/BT** _Update Dec 2022: apparently with the latest kernels (6.0+) these types of issues are gone._ The 2021 model comes with a Mediatek wifi chip which sucks (dropouts and crashes requiring fully powering off the device for minutes), even in Windows 11, and the Bluetooth doesn't work in Linux. Replace it with an Intel AX200 or AX210.  If after replacing it with Intel AX your wifi device disappears from Linux at some point, try a hard power off and reboot into Linux (by holding power button until shut down, while on battery).

# Future...
There are some guys at [Asus Linux](https://asus-linux.org/) doing some great work to improve Linux support on these exceptional laptops.  They work primarily on Arch so they often do not recommended to install their latest work on a production Ubuntu system which may have older packages, and may not be able to help you.  Personally I found it works fine with the Ubuntu 2204+ and kernel 6.0+.  You can join the Asus Linux Discord to be involved or to seek help if you need it.

# Guide to Desktop Linux for Windows Power Users
This is a big guide I wrote, which started off as a bunch of notes that I wrote for myself, and I decided to publish it publically.  It may not always be up to date but it stands as a great reference for advanced Windows users who want to ditch the increasingly toxic Windows world, dont want to live in an expensive walled-garden, and who dont really care too much about AAA gaming.
https://linuxguide.techoneer.com/


# Links
* https://asus-linux.org/
* https://wiki.archlinux.org/title/ASUS_GA401I
* https://rog.asus.com/nz/laptops/rog-zephyrus/2021-rog-zephyrus-g14-series/ Official Asus product page
* https://www.ultrabookreview.com/46631-asus-zephyrus-g14-2021-review/ Benchmarks