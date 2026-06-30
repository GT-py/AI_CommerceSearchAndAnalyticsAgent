export type SQLAgentCell = string | number | null;

export type SQLAgentQueryRequest = {
  question: string;
};

export type SQLAgentQueryResponse = {
  intent: string;
  description: string;
  columns: string[];
  rows: SQLAgentCell[][];
  suggestions: string[];
};
