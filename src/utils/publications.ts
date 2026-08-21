import Papa from "papaparse";
import type { Publication } from "../types/publication";

export type PublicationGroup = [label: string, publications: Publication[]];

export interface PublicationPageData {
	yearGroups: PublicationGroup[];
	typeGroups: PublicationGroup[];
	typeHeadings: Record<string, string>;
}

const UNKNOWN_YEAR = "Unknown";

const TYPE_HEADINGS: Record<string, string> = {
	"Peer-Reviewed Journal Article": "Journal Articles",
	"Peer-Reviewed Conference Paper": "Conference Papers",
	"Non-Peer-Reviewed Conference Presentation":
		"Conference Presentations",
};

const TYPE_ORDER = [
	"Peer-Reviewed Journal Article",
	"Peer-Reviewed Conference Paper",
	"Non-Peer-Reviewed Conference Presentation",
];

function groupPublications(
	publications: Publication[],
	getKey: (publication: Publication) => string,
): PublicationGroup[] {
	const groups = publications.reduce<Record<string, Publication[]>>(
		(groupedPublications, publication) => {
			const key = getKey(publication);
			(groupedPublications[key] ??= []).push(publication);
			return groupedPublications;
		},
		{},
	);

	return Object.entries(groups);
}

function sortYearGroups(groups: PublicationGroup[]): PublicationGroup[] {
	return groups.sort(([yearA], [yearB]) => {
		if (yearA === UNKNOWN_YEAR) return 1;
		if (yearB === UNKNOWN_YEAR) return -1;
		return Number(yearB) - Number(yearA);
	});
}

function sortTypeGroups(groups: PublicationGroup[]): PublicationGroup[] {
	return groups.sort(([typeA], [typeB]) => {
		const indexA = TYPE_ORDER.indexOf(typeA);
		const indexB = TYPE_ORDER.indexOf(typeB);
		const orderA = indexA === -1 ? Number.MAX_SAFE_INTEGER : indexA;
		const orderB = indexB === -1 ? Number.MAX_SAFE_INTEGER : indexB;

		return orderA - orderB || typeA.localeCompare(typeB);
	});
}

export function preparePublicationPageData(
	publicationsCsv: string,
): PublicationPageData {
	const result = Papa.parse<Publication>(publicationsCsv, {
		header: true,
		skipEmptyLines: true,
	});

	if (result.errors.length > 0) {
		throw new Error(
			`Could not parse publications.csv: ${result.errors[0].message}`,
		);
	}

	const publications = [...result.data].sort(
		(a, b) => Number(b.year || 0) - Number(a.year || 0),
	);

	const yearGroups = sortYearGroups(
		groupPublications(
			publications,
			(publication) => publication.year || UNKNOWN_YEAR,
		),
	);

	const typeGroups = sortTypeGroups(
		groupPublications(publications, (publication) => publication.type),
	);

	return {
		yearGroups,
		typeGroups,
		typeHeadings: TYPE_HEADINGS,
	};
}
