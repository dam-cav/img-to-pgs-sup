| Code                                                                                    | Meaning                                                    |
|-----------------------------------------------------------------------------------------|------------------------------------------------------------|
| `CCCCCCCC`                                                                              | One pixel in color C <br> (1 <= C <= 255 `[FF]`)           |
| `00000000` `00LLLLLL` <br> Max -> `3F `                                                 | L pixels in color 0 <br> (1 <= L <= 63 `[3F]`)             |
| `00000000` `01LLLLLL` `LLLLLLLL` <br> Min -> `40` Max -> `7F`, Max -> `FF`              | L pixels in color 0 <br> (64 <= L <= 16383)                |
| `00000000` `10LLLLLL` `CCCCCCCC` <br> Min -> `80` Max -> `BF`                           | L pixels in color C <br> (3 <= L <= 63, 1 <= C <= 255)     |
| `00000000` `11LLLLLL` `LLLLLLLL` `CCCCCCCC` <br> Min -> `C0` Max -> `FF`, Max -> `FF`   | L pixels in color C <br> (64 <= L <= 16383, 1 <= C <= 255) |
| `00000000` `00000000`                                                                   | end of line                                                |