package main

import (
	"context"
	"fmt"
	"math/rand"
	"time"
)

// Question represents a math question
type Question struct {
	Expression string `json:"expression"`
	Answer     int    `json:"answer"`
}

// App struct
type App struct {
	ctx context.Context
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// Greet returns a greeting for the given name
func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, It's show time!", name)
}

// GenerateQuestions generates math questions based on difficulty
func (a *App) GenerateQuestions(difficulty, count int) []Question {
	rand.Seed(time.Now().UnixNano())

	questions := make([]Question, 0, count)
	generated := make(map[string]bool)

	for len(questions) < count {
		q := generateSingleQuestion(difficulty)
		key := q.Expression

		if !generated[key] {
			generated[key] = true
			questions = append(questions, q)
		}
	}

	return questions
}

func generateSingleQuestion(difficulty int) Question {
	switch difficulty {
	case 1:
		return generateLevel1()
	case 2:
		return generateLevel2()
	case 3:
		return generateLevel3()
	case 4:
		return generateLevel4()
	default:
		return generateLevel1()
	}
}

// Level 1: 10以内加减
// 加法：两个加数<10，且和<10
// 减法：被减数<10，减数<10，且差≥0
func generateLevel1() Question {
	isAdd := rand.Intn(2) == 0

	if isAdd {
		// 加法：两个加数1-9，和<10
		a := rand.Intn(9) + 1   // 1-9
		b := rand.Intn(9-a) + 1 // 1 到 (9-a)
		return Question{
			Expression: fmt.Sprintf("%d + %d", a, b),
			Answer:     a + b,
		}
	}
	// 减法：被减数1-9，减数1-9，差≥0
	a := rand.Intn(9) + 1   // 1-9，被减数
	b := rand.Intn(a-1) + 1 // 1 到 a-1，减数
	return Question{
		Expression: fmt.Sprintf("%d - %d", a, b),
		Answer:     a - b,
	}
}

// Level 2: 10以内连加连减混合
// 所有参与运算的数均<10（1-9）
// 运算过程中每一步中间结果及最终结果均<10，且结果≥0
func generateLevel2() Question {
	// 尝试生成，直到找到符合条件的题目
	for {
		// 三个数都在1-9之间
		a := rand.Intn(9) + 1
		b := rand.Intn(9) + 1
		c := rand.Intn(9) + 1

		// 随机选择运算顺序: (a op1 b) op2 c
		op1 := []string{"+", "-"}[rand.Intn(2)]
		op2 := []string{"+", "-"}[rand.Intn(2)]

		// 第一步运算结果
		var step1 int
		if op1 == "+" {
			step1 = a + b
		} else {
			step1 = a - b
		}

		// 中间结果必须>=1且<10（排除0和负数）
		if step1 < 1 || step1 >= 10 {
			continue
		}

		// 第二步运算
		var result int
		if op2 == "+" {
			result = step1 + c
		} else {
			result = step1 - c
		}

		// 最终结果必须>=1且<10（排除0和负数）
		if result < 1 || result >= 10 {
			continue
		}

		return Question{
			Expression: fmt.Sprintf("%d %s %d %s %d", a, op1, b, op2, c),
			Answer:     result,
		}
	}
}

// Level 3: 20以内无需进位、无需借位
// 加法：两个数在11～20之间或一个1-10一个11-20，个位相加<10，不产生进位，且至少有一个>=11
// 减法：被减数或减数至少有一个>=11，被减数个位 ≥ 减数个位，不需借位
func generateLevel3() Question {
	isAdd := rand.Intn(2) == 0

	if isAdd {
		// 加法：至少一个数>=11，个位相加<10，不产生进位，且和<=20
		for {
			a := rand.Intn(20) + 1 // 1-20
			b := rand.Intn(20) + 1 // 1-20
			// 至少一个>=11，个位相加<10，不产生进位，且和<=20
			if (a >= 11 || b >= 11) && (a%10)+(b%10) < 10 && a+b <= 20 && a+b >= 1 {
				return Question{
					Expression: fmt.Sprintf("%d + %d", a, b),
					Answer:     a + b,
				}
			}
		}
	}
	// 减法：至少一个数>=11，被减数个位 >= 减数个位，不需借位
	for {
		a := rand.Intn(20) + 1 // 1-20，被减数
		b := rand.Intn(20) + 1 // 1-20，减数
		// 至少一个>=11，确保 a > b，且被减数个位 >= 减数个位（不需借位）
		if (a >= 11 || b >= 11) && a > b && a%10 >= b%10 {
			return Question{
				Expression: fmt.Sprintf("%d - %d", a, b),
				Answer:     a - b,
			}
		}
	}
}

// Level 4: 20以内需要进位、需要借位
// 加法：至少一个数>=11，个位相加≥10，必须进位
// 减法：被减数或减数至少有一个>=11，被减数个位 < 减数个位，必须借位
func generateLevel4() Question {
	isAdd := rand.Intn(2) == 0

	if isAdd {
		// 加法：至少一个数>=11，个位相加≥10，必须进位
		for {
			a := rand.Intn(20) + 1 // 1-20
			b := rand.Intn(20) + 1 // 1-20
			// 至少一个>=11，个位相加>=10，且和<=20
			if (a >= 11 || b >= 11) && (a%10)+(b%10) >= 10 && a+b <= 20 {
				return Question{
					Expression: fmt.Sprintf("%d + %d", a, b),
					Answer:     a + b,
				}
			}
		}
	}
	// 减法：至少一个数>=11，被减数个位 < 减数个位，必须借位
	for {
		a := rand.Intn(20) + 1 // 1-20，被减数
		b := rand.Intn(20) + 1 // 1-20，减数
		// 至少一个>=11，确保 a > b，且被减数个位 < 减数个位（需要借位）
		if (a >= 11 || b >= 11) && a > b && a%10 < b%10 {
			return Question{
				Expression: fmt.Sprintf("%d - %d", a, b),
				Answer:     a - b,
			}
		}
	}
}
