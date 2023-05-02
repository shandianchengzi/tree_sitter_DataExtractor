
using System.Numerics;
/// <summary>
/// 扩展欧几里德算法
/// </summary>
/// <param name="e">公钥（加密指数）</param>
/// <param name="l">p-1与q-1的最小公倍数</param>
/// <returns></returns>
/// <exception cref="ArgumentException"></exception>
///
public class Kuozhan
{
    int n = 9;
    public BigInteger Euclidean(BigInteger e, BigInteger l)
    {
        int m = n + 1;
        for(int i = 0; i < m; i++)
        {
            ;
        }
        if (e > l)
        {
            throw new ArgumentException("e不能大于l");
        }

        var gcd = BigInteger.GreatestCommonDivisor(e, l);
        if (gcd != 1)
        {
            throw new ArgumentException("e与l必须互质");
        }

        return Euclidean(e, l, out _, out _);
    }

    public BigInteger Euclidean(BigInteger e, BigInteger l, out BigInteger d, out BigInteger k)
    {
        d = k = 1;
        if (l > e)
        {
            var remainder = l % d;
            if (remainder == 0)
            {
                k = 0;
                d = 1;
            }
            else
            {
                Euclidean(e, remainder, out _, out k);
                d = (l * k + 1) / e;
            }
            return e;
        }
        else
        {
            var remainder = e % l;
            if (remainder == 0)
            {
                e = 0;
                k = 1;
            }
            else
            {
                Euclidean(remainder, l, out d, out _);
                k = (e * d + 1) / k;
            }
            return k;
        }
    }
}
