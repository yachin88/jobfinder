# Job Circular Monitor

Website link diye rakhle, oi site-e notun kono link/notice ashle email-e notify korbe. Free GitHub Actions e cholbe — nijer PC on rakhar dorkar nai.

## Setup (5 step)

### 1. Gmail App Password banao
- Gmail account e 2-Step Verification on koro (https://myaccount.google.com/security)
- https://myaccount.google.com/apppasswords e giye ekta 16-digit App Password generate koro
- Eta save rakho, next step e lagbe

### 2. GitHub repo banao
- GitHub e notun private repo banao (e.g. `job-monitor`)
- Ei folder er shob file upload/push koro

### 3. Secrets add koro
Repo → Settings → Secrets and variables → Actions → New repository secret:
- `EMAIL_FROM` = tomar gmail address (jekhan theke email jabe)
- `EMAIL_APP_PASSWORD` = step 1 er 16-digit app password
- `EMAIL_TO` = kon email e notification pete chao (nijer email o hote pare)

### 4. urls.txt e link dao
`urls.txt` file khule tomar job circular website gulor link dao, ek line e ekta.

### 5. Test run koro
Repo → Actions tab → "Job Circular Monitor" workflow select koro → "Run workflow" button chapo.
- Prothom run e শুধু baseline save hobe (email আসবে না, কারণ কিসের সাথে compare korbe eta ekhono nai)
- Second run theke notun link ashle email pabe

## Kivabe kaj kore
- Prottek 6 ghonta por por (cron) automatic check hoy — GitHub Actions free tier e ei kaj covered
- Script prottek URL er link list save kore rakhe (`state.json`)
- Next run e comparison kore — notun link paile email pathay, naile chup thake
- Je kono somoy "Run workflow" diye manually o check koraite paro

## Frequency change korte chaile
`.github/workflows/job-monitor.yml` file e ei line ta:
```
- cron: "0 */6 * * *"
```
Ei duita popular option:
- Every 1 hour: `0 * * * *`
- Once a day (sokal 8ta): `0 2 * * *` (UTC time, Bangladesh time theke 6 ghonta pichone)

## Note
- Ei script link/text change track kore. Kono site jodi JavaScript diye content load kore (link direct HTML e na thake), tahole eta miss korte pare — emon site thakle bolo, Selenium/Playwright diye adjust kore dibo.
