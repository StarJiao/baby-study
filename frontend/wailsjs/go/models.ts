export namespace main {
	
	export class Question {
	    expression: string;
	    answer: number;
	
	    static createFrom(source: any = {}) {
	        return new Question(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.expression = source["expression"];
	        this.answer = source["answer"];
	    }
	}

}

