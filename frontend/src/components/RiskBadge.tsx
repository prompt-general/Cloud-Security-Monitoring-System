type Props = {
	severity: "high" | "medium" | "low";
};

export default function RiskBadge({ severity }: Props) {
	const cls = severity === "high" ? "badge badge-high" : "badge badge-medium";
	return <span className={cls}>{severity.toUpperCase()}</span>;
}
