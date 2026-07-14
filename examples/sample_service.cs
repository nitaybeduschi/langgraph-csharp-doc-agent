using System;

namespace ExampleApp
{
    public class SampleService
    {
        public string GetGreeting(string name)
        {
            return $"Hello, {name}!";
        }

        public int Add(int a, int b)
        {
            return a + b;
        }
    }
}
