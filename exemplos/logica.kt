fun main()
  val a = true
  val b = false

  if a or b
    println("um_deles_verdadeiro")

  if a and not b
    println("totalmente_verdadeiro")

  val teste = a and b or a
  if teste
    val teste_ok = "passou"
    println(teste_ok)
