fun fatorial(n: Int)
  var resultado = 1
  var i = n
  while i > 1
    resultado = resultado * i
    i = i - 1
  return resultado

fun main()
  val fat5 = fatorial(5)
  println(fat5)
