def solve(s, i, j, dp):

    if i == len(s) or j == -1:

        return 0

    if dp[i][j] != 0:

        return dp[i][j]

    if s[i] == s[j]:

        dp[i][j] = solve(s, i + 1, j - 1, dp) + 1

    else:

        dp[i][j] = max(solve(s, i, j - 1, dp), solve(s, i + 1, j, dp))

    return dp[i][j]



r = input().strip()

n = len(r)

s = r[::-1]

    

dp = [[0] * (n + 1) for _ in range(n + 1)]

    

for i in range(1, n + 1):

   for j in range(1, n + 1):

       if s[i - 1] == r[j - 1]:

           dp[i][j] = dp[i - 1][j - 1] + 1

       else:

           dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    

print(dp[n][n])