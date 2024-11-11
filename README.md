# ReBoi
Respositry for ReBoi files and configs

Setting Up RetroPie 4.8 headlessly:

Flash Retropie image to SD card

create directory on SD card Boot called ssh

create `wpa_supplicant.conf`

```
country=YOUR_COUNTRY_CODE
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOUR_SSID"
    psk="YOUR_PASSWORD"
    key_mgmt=WPA-PSK
}
```
