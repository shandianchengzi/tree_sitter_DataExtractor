using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace TestProject
{
    class Program
    {
        static int classVar = 23;

        static void Bar(string a)
        {
            string b = a;
            if (a == null) return;
            if (b == null) return;
            return;
        }

        static void Main(string[] args) {
            var foo = args[0];
            foo.StartsWith("foobar");
            Bar(foo);
            Class1.TestClass(foo);
        }

        
    }
}
