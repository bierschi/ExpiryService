# ExpiryService
Receive notifications when provider services expires

**Features** of [ExpiryService]():
- Receive notifications when services expires
- Provides an API interface to dynamically update provider data
- Get Mail or Telegram notifications
- Supports Provider AldiTalk and Netzclub

## Installation

install [ExpiryService]() with pip

<pre><code>
pip3 install ExpiryService
</code></pre>

or from source 
<pre><code>
sudo python3 setup.py install
</code></pre>


## Usage and Examples

Print the available arguments for ExpiryService
<pre><code>
ExpiryService --help
</code></pre>

## API

## Logs

logs can be found in `/var/log/ExpiryService`

## Troubleshooting
add your current user to group `syslog`, this allows the application/scripts to create a folder in
`/var/log`. Replace `<user>` with your current user
<pre><code>
sudo adduser &lt;user&gt; syslog
</code></pre>
to apply this change, log out and log in again and check with the terminal command `groups`

## Changelog
All changes and versioning information can be found in the [CHANGELOG](https://github.com/bierschi/ExpiryService/blob/master/CHANGELOG.rst)



