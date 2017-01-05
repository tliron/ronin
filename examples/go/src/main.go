package main

import "fmt"
import . "ronin/functions"

func main() {

    // Call a function just as you'd expect, with
    // `name(args)`.
    res := Plus(1, 2)
    fmt.Println("1+2 =", res)

    res = PlusPlus(1, 2, 3)
    fmt.Println("1+2+3 =", res)
}
