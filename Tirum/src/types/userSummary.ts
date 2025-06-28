export interface UserSummary {
  total_to_take: number;
  total_to_return: number;
  to_take_with: Array<{
    borrower__username: string;
    total: number;
  }>;
  to_return_with: Array<{
    lender__username: string;
    total: number;
  }>;
  transactions: Array<Transaction>;
}

export interface Transaction {
  id: number;
  amount: number;
  description: string;
  category: string;
  date: string;
  paid_by: number;
  split_details: Array<SplitDetail>;
}

export interface SplitDetail {
  id: number;
  user: number;
  amount: number;
  percentage: number;
}

export interface SummaryCard {
  title: string;
  value: string;
  icon: string;
  color: string;
  change?: string;
} 