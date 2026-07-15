
### Case Study

> A few days ago I came across `NormalCrackme.exe` on [crackmes.one](https://crackmes.one/crackme/697f67fe977274421cc111ef) — a beginner-level reverse engineering challenge by BadEngineer. The description promised a simple password check, so I decided to use it as a warm-up exercise and document the analysis process. What caught my attention was not just the validation algorithm, but a subtle stack-related behavior that looks like a security check but does not actually prevent memory corruption.

### Sample Information

| Field        | Value                                                              |
| ------------ | ------------------------------------------------------------------ |
| Filename     | `NormalCrackme.exe`                                                |
| SHA256       | `7bb6b820296eaf4a1db786934bbbaf09f35b62c561b5291c5081282662959da1` |
| Arch         | x86-64                                                             |
| Size         | 435.03 KB                                                          |

### Technical Analysis
#### Main Logic — A Simple Loop with a Trap

The program follows a straightforward flow: initialize the C runtime, prompt the user for a password, and enter a validation loop. If the `Checker` function rejects the input, the user gets another attempt — unless the input is longer than 13 characters, in which case the program prints a warning.

<img width="777" height="359" alt="изображение" src="https://github.com/user-attachments/assets/3013b46d-773c-4892-961a-f271938bfb8e" />


At first glance, the `strlen(Str) > 13` check appears to protect against oversized input. However, this is a **post-write validation**: `scanf` has already written the data to the stack before the length is ever checked. Depending on compiler padding and stack alignment, this may overwrite the saved frame pointer or return address.


#### The Checker — Character Class Counting

The `Checker` function implements a custom validation algorithm based on ASCII range checks. Rather than comparing the input against a hardcoded string, it counts how many characters fall into four categories and expects exact quotas.

The obfuscated IDA pseudocode uses nested `if` statements to classify each character. After deobfuscation, the logic is clean:

|               |      ASCII Range (dec)       |             ASCII Range (hex)              |            Characters             | Required Count |
| ------------- | :--------------------------: | :----------------------------------------: | :-------------------------------: | :------------: |
| **Digits**    |           48 – 57            |                0x30 – 0x39                 |               0 – 9               |       3        |
| **Uppercase** |           65 – 90            |                0x41 – 0x5A                 |               A – Z               |       3        |
| **Lowercase** |           97 – 122           |                0x61 – 0x7A                 |               a – z               |       4        |
| **Specials**  | 33–47, 58–64, 91–96, 123–127 | 0x21–0x2F, 0x3A–0x40, 0x5B–0x60, 0x7B–0x7F | !"#$%&'()*+,-./:;<=>?@[\]^_{\|}~` |       3        |

**Total length:** 3 + 3 + 4 + 3 = **13 characters**.

This means any 13-character string that satisfies the quotas above will be accepted. There is no cryptographic hashing, no entropy check — just a simple counting routine.

#### Validation Logic

To verify my understanding, I reproduced the algorithm in Python:

<img width="565" height="275" alt="изображение" src="https://github.com/user-attachments/assets/f9145a3f-8eaa-441f-aad9-6a26076ff8ef" />


### Solution

Using the constraints above, I generated a valid password:
> E|pbzZ!1X6g7&

The program accepted the input and printed:
> Good job, You Really Cracked it!

For completeness, I also wrote a keygen that produces random valid passwords:

<img width="589" height="325" alt="изображение" src="https://github.com/user-attachments/assets/d6cb8868-e896-4cb9-9ca7-bda03429a202" />



### Security Notes

> **CWE-120: Buffer Copy without Checking Size of Input**
> Static analysis of `main` reveals that `scanf("%s", Str)` writes user input into a fixed 13-byte stack buffer without length restriction. The subsequent `strlen(Str) > 13` check is a **post-write validation** — it executes after the overflow has already occurred.
> 
> **Dynamic verification:** To confirm stack corruption, I provided an input of 1,000+ characters. The program immediately crashed with an access violation, indicating that the return address or saved frame pointer was overwritten. In smaller inputs (30–50 characters), the MinGW compiler’s stack padding masked the corruption, allowing the program to continue execution. This demonstrates that the vulnerability is **real but layout-dependent** — a behavior commonly observed in early-stage malware where "fake" bounds checks create a false sense of security.

### Conclusion

> `NormalCrackme.exe` is a textbook example of a beginner reverse engineering challenge. Its validation algorithm — character class counting — is easy to reverse once the nested `if` obfuscation is flattened. However, the real learning point was the `scanf`/`strlen` pattern: a check that looks like a guard but is actually a post-hoc observation.
> 
> From a malware analysis perspective, this pattern is relevant because poorly written credential harvesters and early-stage loaders often use similar "fake" bounds checks. Recognizing that the dangerous write happens **before** the validation is a skill that translates directly to finding real vulnerabilities in the wild.
