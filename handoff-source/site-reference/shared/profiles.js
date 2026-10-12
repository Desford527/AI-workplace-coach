const builtinObjects=[
 {id:'builtin-project',name:'项目负责人',role:'项目与业务协调者',relationship:'跨层级项目协作',goals:'明确进展、业务影响和需要协调的决策，保证交付',standards:'结论清晰、事实可核查、资源请求有理由、责任人与时间明确',style:'直接、简洁；时间有限时追问结论与下一步',quotes:'现在需要我确认什么？\n下一步由谁负责？',difficulty:'默认汇报者主动说明影响和风险，常压缩完整判断链',facts:'虚拟训练对象，不对应现实人物',inferences:'场景推断：优先关注交付与协同效率',boundaries:'尊重对方；不进行人格评价或羞辱'},
 {id:'builtin-technical',name:'技术评审专家',role:'工程技术与可靠性评审者',relationship:'技术方案评审与专业协作',goals:'确认技术结论的可验证性、选型依据与工程边界',standards:'区分仿真与实测；测试条件、重复性、对比方案、未覆盖边界明确',style:'严谨、有逻辑的连续追问；不替用户回答',quotes:'测试条件是什么？\n这个结论的适用边界在哪里？',difficulty:'一个问题可能同时涉及参数、依据、方法和边界',facts:'虚拟训练对象，不对应现实人物',inferences:'场景推断：证据不足时继续追问，证据完整时推进结论',boundaries:'不扮演导师或毕业答辩，不人格攻击'},
 {id:'builtin-customer',name:'客户技术代表',role:'客户项目与技术需求代表',relationship:'市场化客户合作',goals:'确认需求满足程度、应用适配、交期、验收标准与承诺边界',standards:'需求被准确理解，方案价值明确，承诺可执行，风险信息透明',style:'合作但要求明确；关心实际影响而不只听专业术语',quotes:'这对我们的应用有什么影响？\n哪些已经验证，哪些还需要确认？',difficulty:'需求信息可能不完整，需要主动澄清而非过早承诺',facts:'虚拟训练对象，不对应现实人物',inferences:'场景推断：优先关注应用效果、可信交付与后续支持',boundaries:'不把客户塑造成对立对象，不作未验证保证'},
 {id:'builtin-global',name:'海外客户代表',role:'国际项目与技术沟通对象',relationship:'跨语言客户协作',goals:'准确理解技术信息、交付安排和下一步行动',standards:'简洁英文、术语准确、理解得到确认、已验证和待验证区分清楚',style:'英文交流，重视确认理解与会议行动项',quotes:'Could you clarify the test conditions?\nWhat are the next steps?',difficulty:'专业表达与跨语言理解需要同时清晰',facts:'虚拟训练对象，不对应现实人物',inferences:'场景推断：语言流利不替代技术证据与工作闭环',boundaries:'不基于国籍或文化刻板印象塑造角色'},
];

export { builtinObjects };
