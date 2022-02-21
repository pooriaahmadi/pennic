## What is Pennic?

Pennic is a peer-to-peer-ish digital currency that enables you to send money
online. It's also a distributed and decentralised network.

## Goals & motto

- 1 PEN > 1 BTC
- All digital but safe

## Getting started

Follow the instructions below, and experience the thrill of being an early
adopter without any of the guilt of doing something that you deeply don't
believe in.

The quickstart assumes (for now) that you have Python up and running. _The instructions below are written with
Linux/POSIX in mind._

- If you're a MacOS user, it is presumed that you have `python3` installed (either by e.g. using `pyenv`, or using a recent version of macOS).
- If you're a Windows user, remember to use `Scripts\activate.bat` instead of `.bin/activate`.

```bash
# Installing:
$ python3 install pipenv
$ pipenv install
$ pipenv scripts
$ pipenv run generate_keys
# This will create your private and public key
$ pipenv run setup_database
# This will create the blockchain database on your pc
$ pipenv run benchmark
# After running this you'll be given a number that is a measurement for how many hashes percycle gives you the best performance
$ touch .env
$ echo "HOST=localhost PORT=34756 BLOCKCHAIN_DATABASE_PATH=blockchain.db HASH_RATE=5500 DEVELOPMENT=1 RECENT_NODES_FILE_PATH=recent_nodes.json NODES_ASK_LIMIT=10" | tr " " "\n" >> .env
# Please replace HASH_RATE with the number in the benchmark command
```

Note that pennic's scripts will create whatever files they need to operate
right in the directory where they're being called. This includes your wallet.

## Get coin

Pennic is a "early phase" coin. This means you can probably mine some yourself, as per the instructions above.

If you have ethical objections against this, you can always go to the
[faucet](https://github.com/pooriaahmadi/pennic/issues/1) to get some free coin.

## Frequently Asked Questions

**Q:** Is this a real coin?

**A:** Pennic is every bit as real as Bitcoin and its many clones.

---

**Q:** Is this some kind of joke?

**A:** You can laugh all you want, but we all know you're just trying to hide your fear of missing out.

---

**Q:** Is it safe to put my life savings into pennic?

**A:** [No](https://github.com/pooriaahmadi/pennic/blob/master/docs/security.md)

---

## Frequently raised objections

**O:** I can't buy pennic at an exchange -- this means it's not a "real" coin!

**A:** You have that exactly backwards: Skepticoin is a peer-to-peer digital currency, which means it's independent from
established financial institutions such as exchanges. This independence is precisely its strength! You aren't
trying to suggest that cryptocurrency's main claim to fame is untrue, are you?

---

**O**: If you're so against cryptocurrency, starting a coin of your own is hypocritical.

**A**: The ability to hold 2 directly opposing thoughts in your head is the core of cryptocurrency. If you can't do that
then this indeed isn't for you.

---

**O**: This thing is fugly and way too technical. It will never gain traction among a sufficiently large group of fools
without a pretty GUI.

**A**: Patience, young grasshopper, everything at its time. First we bring in the techies who bring their thorough
understanding of crypto-nonsense and steadfast determination to bring it all down to the ground. The tech
illiterate are only allowed to join the lower ranks of the pyramid, so that GUI must wait a bit.

## Getting involved

The best places to find other Pennics are

- [The Skepticoin Subreddit](https://www.reddit.com/r/pennic/) (use [old.reddit.com to avoid the popup on
  mobile](https://old.reddit.com/r/pennic/) if you don't have a Reddit account.)

- [Discord](https://discord.gg/SsyE7QCcTJ)

## Contributing:

Some ways you can contribute to this project:

- Spread the news. ([Remember the first principle](https://github.com/pooriaahmadi/pennic/blob/master/docs/philosophy/principles.md))
- [Set up port forwarding on your router](https://github.com/pooriaahmadi/pennic/blob/master/docs/port-forwarding.md)
- [File a bug](https://github.com/pooriaahmadi/pennic/issues/new) if you have one
- Open a PR (but make sure to read
  [CONTRIBUTING.md](https://github.com/pooriaahmadi/pennic/blob/master/CONTRIBUTING.md) first
