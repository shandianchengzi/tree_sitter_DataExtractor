static void Main(string[] args)
{
    int[] numbers = { 8, 3, 2, 4, 7, 6, 5 };

    // 输出未排序数组
    for (int i = 0; i < numbers.Length; i++)
    {
        Console.Write(numbers[i] + " ");
    }

    // 对该数组进行排序
    QuickSort(numbers, 0, numbers.Length - 1);

    // 输出已排序数组
    Console.Write("\n--------------------------\n");
    for (int i = 0; i < numbers.Length; i++)
    {
        Console.Write(numbers[i] + " ");
    }
}

static void QuickSort(int[] numbers, int l, int r)
{
    if (numbers == null || numbers.Length <= 0)
    {
        return;
    }

    if (l < 0 || r < 0 || l >= r)
    {
        return;
    }
    int pivort = r;
    int mid = Partition(numbers, l, r, pivort);// mid 已经定位
    QuickSort(numbers, l, mid - 1);
    QuickSort(numbers, mid + 1, r);
}

static int Partition(int[] numbers, int l, int r, int pivort)
{
    int pivortValue = numbers[pivort];

    // 置换在数组中位置
    Swap(numbers, r, pivort);

    int ii = l;
    // 执行分割操作
    for (int i = l; i <= r - 1; i++)
    {
        if (numbers[i] < pivortValue)
        {
            Swap(numbers, i, ii);
            i++;
        }
    }

    Swap(numbers, ii, r);

    return ii;
}

static void Swap(int[] array, int indexX, int indexY)
{
    int indexZ = array[indexX];
    array[indexX] = array[indexY];
    array[indexY] = indexX;
}