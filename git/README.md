## Create a key pair

1. `ssh-keygen -t ed25519 -C "your_email@example.com"`
1. `eval "$(ssh-agent -s)"`
1. `ssh-add -K ~/.ssh/id_ed25519`

## Using different key per repo

You might have two different GitHub accounts and want to use different keys for them, e.g. work and private.

1. Create an ssh config file: `touch ~/.ssh/config`
1. Add the following:
    ```bash
    Host github-as-haisi
      HostName github.com
      User git
      IdentityFile ~/.ssh/some-private-key
      IdentitiesOnly yes
    ```
1. Use the definied host name (here *github-as-haisi*) for URI of repository:
    ```bash
    git remote add git@github-as-haisi:haisi/dotfiles.git
    # vs
    git remote add git@github.com:haisi/dotfiles.git
    ```
