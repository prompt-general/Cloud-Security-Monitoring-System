type Activity = {
	timestamp: string;
	description: string;
};

type Props = {
	activity: Activity[];
};

export default function UserActivityTimeline({ activity }: Props) {
	return (
		<ul className="timeline">
			{activity.map((item) => (
				<li key={`${item.timestamp}-${item.description}`}>
					<strong>{new Date(item.timestamp).toLocaleString()}</strong>
					<div>{item.description}</div>
				</li>
			))}
		</ul>
	);
}
