# Advanced Scene Switcher Token usage Examples

This describes a few of the common possible usages of the adv-ss token.\
If you have ideas for additions to this, you are more than welcome to suggest them, either as a PR on this repo if you want to write it yourself, or as an issue/Discord message if you'd rather not.\
*N.B.: This requires having the [Advanced Scene Switcher](https://obsproject.com/forum/resources/advanced-scene-switcher.395/) plugin installed.*

## Twitch Info

The following macro allows using a Twitch channel's info into the filename formatting.\
All you need is to fill in the channel name, ad to create and select a twitch connection.

![Twitch info macro](https://github.com/Penwy/adv-ff/blob/main/docs/twitch_info_macro.png)

Once that is done, the formatting token `a$twitch_game_name$` will then fill in with the current category selected on the specified channel.\
More variables can be added for other info one might want.

You can directly import this macro with the code below.
```
AAAORnicxVfdTyM3EP9XVlYf2ms2TQIHgTeOS3WRjo8CpQ8VQmY92bjs2ivbG+AQ/3tn7P1wQqBqH3qRELvj+Z7fzHifWckzoy07/POZKV4CO2RcrNLFInEP0mXLRKqFZgOWG11X7HDBCwsDVvHawiVfwSdY8pXUhh2OGmrEY3hRQMEOnanxPVtCdn+slZBOamXn6rxjaCS0Ol5ylUMrYe9lNXuE7ExdOm5cx2edro6yoGVxqt1nrXqz5NhSG3csTVZLN1vxoubEG3Mc16ij7Jw5JtfmyoFB7o4ve5fpmZFmiB5Gw8nBxm/A3FNFRy9oVknn07QCY70/Y6QKnd1fgnNS5ZZ0GcilRRtRsFwJXmCIn5G1TQ2J/SGV0A9YMH8wYEtuL2r1qXaOlAc+pJ1TVV5RMaOutl/5XZT/pcyXBf65+aKv05Wp++SaVv8VPGIwDO2xpu5rdG+TUcyvz34PNDzN1owEjxqm3n7CDSTk9nBN4ldy6D0R7zHJUKrmIuDa2tTjPSViOh1n0wNxsJ/u7e9k6e7OdJIeZNNpKnanY/FxurcPfJdt1MuLB/B1Bi+rQjqs2bm2MiANm6miptrZ+fgyaJ4nu+OXm0bBDH0LSt6WnYwOOtkRSbbQ+KLdPTzZ9WYMRJS+6bIek5zO8wLON8l9Pr1dC3kJysV4zHRR8MqCeN0+6+DJYho7eUoK/zhgoPhdQfIBe2vZlFQXJ0vE+4AVOpeZ7xBRG9+yJ1rIhaRmePZct+ivdYZLFTrJAgVgtzfj6J+a76Vj6C1uUzXZpmq82ceNgsl/dIbKW2JgmHd8nXgJiwP2oqfG5RbR0AS71P1wjHV+t4r61dGXdDya/I9F7UBNhv2P8H8P+M7mClVJ0S63QKbdxJUCP9WbJchQUaXRJ3sBD9wIOvKxpcjupCvAP7/QgDbAy6uGNKMFkQQG37Lw2Bw9N3mLF6STvNuPumoakUJDh9wJWMtzbFqaDx6ZZaCgmeGHVnusOCh6T29ldAV4DNTwN2SIO8i1eWrjSxHYTQp8dFkB3HyqFwswZ+qEU1m3IA1HCc++9xxZcSN9Hgbd42mIJFT7Nse3Wx9czzFpWFpgtPTEQgE+JOZLfB0QyPBN1eX1+8CMEbg3aNMxF48hv7a+u3QGM9Nca3o1sZKeS36Dt5g8BDqERLDwpfIWtwsu8PJwsYmfTWC2IyZGEAmiX2iM9i52UEIUb7YqeAbrZw0xwQIsW9dwby5k/i8bouRuOXusDHaAzyv7MRknPyeT5EOyk/yU/JLQpu4gdW50WfUzUaqqdi2NHaGKXCU+K+RjW/LDoGHumcnrpS5EdBOTrw5YmkLodww3TT1IV9JoReW+Xsfgl7OTGUEpAwWXHbZoBrY7qJ081JSIRhtxsRMcj9SODsoKFfdyYwL/Y/MfGWOMC6gw668WjXdhjprmSkAMkHEMECFNa33kOwCR+BVUThq3S1RcCGTCOzz6tzulMCxctdEZvMbq8rQu78C8wv16+8SsMyVie6MN1hxDwbUCdC/PqSQBOn9ZrX6rgcYa+2FodQlDXJMOxDAoChyb8a9pXp9u0F3YbLg5eTC0JQ7D9KafKmvfUw4ts7DNj5qM0u2hGSgVJhY/dNytL9iC14XrZg1t8EaJAPj2tpI7fYcfcfZ9FVumYKxutEW4m+uYzBqa0LvMsPFwZzLcZS9/A1v53LM=
```
